import shutil
import os
from typing import Any, Optional
from datasets import Dataset
from huggingface_hub import HfApi
import pandas as pd
from pathlib import Path
try:
    from auto_gptq import AutoGPTQForCausalLM, BaseQuantizeConfig
    from peft import prepare_model_for_kbit_training, PeftModel
    from peft import AutoPeftModelForCausalLM
    from peft import LoraConfig, get_peft_model
    import torch
    import torch.nn as nn
    from transformers import (
        AutoTokenizer, 
        AutoModelForCausalLM, 
        BitsAndBytesConfig, 
        Trainer, 
        TrainingArguments, 
        DataCollatorForLanguageModeling,
    )
except ImportError:
    pass


def create_labels(input_ids, eos_token, separator=[518, 29914, 25580, 29962]):
    if not isinstance(input_ids, torch.Tensor):
        input_ids = torch.tensor(input_ids)
    if not isinstance(separator, torch.Tensor):
        separator = torch.tensor(separator)

    separator_len = separator.size(0)
    input_len = input_ids.size(0)
    start = 0
    end = input_len
    for i in range(input_len):
        if not i + separator_len > input_len:
            if torch.all(input_ids[i:i+separator_len] == separator):
                start = i + separator_len
        if input_ids[i] == eos_token:
            end = i
            break
    if end < input_len:
        end += 1

    labels = torch.full_like(input_ids, -100)
    labels[start:end] = input_ids[start: end]
    return labels


class BaseRoutine:
    def __init__(
        self,
        train_data,
        model_name,
        base_model='meta-llama/Llama-2-7b-chat-hf',
        training_args={},
        eval_data=None,
        quantization_config=None,
        lora_config=None,
        train_on_prompts=True,
        max_length=1024,
        hf_token=None,
        adapters_name=None,
        quantized_name=None,
        **kwargs,
    ):
        if 'output_dir' not in training_args:
            training_args['output_dir'] = 'outputs'
        self.train_data = train_data
        self.model_name = model_name
        self.base_model = base_model
        self.training_args = training_args
        self.eval_data = eval_data
        self.quantization_config = quantization_config
        self.lora_config = lora_config
        self.train_on_prompts = train_on_prompts
        self.max_length = max_length
        self.hf_token = hf_token
        
        self.adapters_name = adapters_name if adapters_name is not None else model_name + '-adapters'
        self.quantized_name = quantized_name if quantized_name is not None else model_name + '-GPTQ'
        if isinstance(self.train_data, list):
            self.train_data = pd.DataFrame(self.train_data)
        if isinstance(self.eval_data, list):
            self.eval_data = pd.DataFrame(self.eval_data)
        self.tokenizer = self.load_tokenizer()

    def get_trainer_class(self):
        if self.train_on_prompts:
            class CustomTrainer(Trainer):
                def compute_loss(self, model, inputs, return_outputs=False):
                    inputs['labels'] = inputs['input_ids']
                    return super().compute_loss(model, inputs, return_outputs)
        else:
            class CustomTrainer(Trainer):
                def compute_loss(self, model, inputs, return_outputs=False):
                    inputs['labels'] = [
                        create_labels(
                            inputs['input_ids'][i].detach().cpu(),
                            eos_token=self.tokenizer.eos_token,
                        ).reshape(1, -1)
                        for i in range(inputs['input_ids'].size(0))
                    ]
                    inputs['labels'] = torch.concat(inputs['labels']).to(model.device)
                    return super().compute_loss(model, inputs, return_outputs)
        return CustomTrainer

    def load_tokenizer(self):
        tokenizer = AutoTokenizer.from_pretrained(
            self.base_model, 
            use_fast=False,
        )
        tokenizer.pad_token = tokenizer.eos_token
        return tokenizer

    def load_model(self):
        model_args = {
            'torch_dtype': torch.float16,
            'device_map': 'auto',
        }

        if self.quantization_config:
            model_args['quantization_config'] = BitsAndBytesConfig(**self.quantization_config)

        model = AutoModelForCausalLM.from_pretrained(
            self.base_model,
            **model_args,
        )

        if self.lora_config:
            lora_config = LoraConfig(**self.lora_config)
            model.gradient_checkpointing_enable()
            model = prepare_model_for_kbit_training(model)
            model = get_peft_model(model, lora_config)
            class CastOutputToFloat(nn.Sequential):
                def forward(self, x): return super().forward(x).to(torch.float32)
            model.lm_head = CastOutputToFloat(model.lm_head)

        return model

    def load_dataset(self, data):
        def tokenize_text(example):
            return self.tokenizer(example['text'], truncation=True, max_length=self.max_length)
        data = data[['text']]
        return Dataset.from_pandas(data).map(tokenize_text, batched=True)
    
    def get_trainer_class_args(self):
        return {
            'data_collator': DataCollatorForLanguageModeling(self.tokenizer, mlm=False),
        }

    def train(self, push=True):
        train_dataset = self.load_dataset(self.train_data)
        eval_dataset = None if self.eval_data is None else self.load_dataset(self.eval_data)

        trainer_class_args = self.get_trainer_class_args() 
        if eval_dataset is not None:
            trainer_class_args['eval_dataset'] = eval_dataset

        model = self.load_model()

        trainer_class = self.get_trainer_class()
        trainer = trainer_class(
            args=TrainingArguments(
                **self.training_args
            ),
            model=model,
            tokenizer=self.tokenizer,
            train_dataset=train_dataset,
            **trainer_class_args
        )
        
        model.config.use_cache = False
        trainer.train()

        if eval_dataset is not None:
            trainer.evaluate()

        trainer.save_model(self.training_args['output_dir'])
        if push:
            self.tokenizer.push_to_hub(self.adapters_name, private=True)
            trainer.model.push_to_hub(self.adapters_name)

    def process_merge_args(self, merged_model_path=None, merged_name=None, offload_path=None):
        if merged_model_path is None:
            merged_model_path = Path(self.training_args['output_dir']) / 'merged_model'
        merged_model_path = Path(merged_model_path)
        if merged_name is None:
            merged_name = self.model_name
        if offload_path is None:
            offload_path = Path(self.training_args['output_dir']) / 'offload'
        offload_path = Path(offload_path)
        return merged_model_path, merged_name, offload_path

    def push_merged_model(self, merged_model_path=None, merged_name=None):
        merged_model_path, merged_name, _ = self.process_merge_args(merged_model_path, merged_name)
        self.tokenizer.push_to_hub(merged_name, private=True)
        api = HfApi()
        api.upload_folder(
            repo_id=merged_name,
            folder_path=merged_model_path,
        )
        
    def merge(self, merged_model_path=None, merged_name=None, offload_path=None, push=True):
        merged_model_path, merged_name, offload_path = self.process_merge_args(merged_model_path, merged_name, offload_path)

        print("Merging and saving model, this can take a while")
        model = AutoPeftModelForCausalLM.from_pretrained(
            self.adapters_name, 
            torch_dtype=torch.float16,
            device_map='auto',
            offload_folder=offload_path,
        )
        model = model.merge_and_unload(progressbar=True)

        if merged_model_path.exists():
            shutil.rmtree(merged_model_path)
        merged_model_path.mkdir(exist_ok=True, parents=True)
        
        self.tokenizer.save_pretrained(merged_model_path)
        model.save_pretrained(merged_model_path, safe_serialization=True)
        model.config.save_pretrained(merged_model_path)

        if push:
            self.push_merged_model(merged_model_path, merged_name)

    def process_quantize_args(self, quantized_model_path=None, quantized_name=None, merged_name=None):
        if quantized_model_path is None:
            quantized_model_path = Path(self.training_args['output_dir']) / 'quantized_model'
        quantized_model_path = Path(quantized_model_path)

        if quantized_name is None:
            quantized_name = self.quantized_name

        if merged_name is None:
            merged_name = self.model_name
        return quantized_model_path, quantized_name, merged_name

    def push_quantized_model(self, quantized_model_path=None, quantized_name=None):
        quantized_model_path, quantized_name, _ = self.process_quantize_args(
            quantized_model_path, quantized_name,
        )
        self.tokenizer.push_to_hub(quantized_name, private=True)
        api = HfApi()
        api.upload_folder(
            repo_id=quantized_name,
            folder_path=quantized_model_path,
        )
        
    def quantize(
        self, 
        examples=None, 
        num_examples=128, 
        gptq_config=None,
        quantized_model_path=None, 
        quantized_name=None, 
        merged_name=None, 
        push=True,
    ):
        quantized_model_path, quantized_name, merged_name = self.process_quantize_args(
            quantized_model_path, quantized_name, merged_name
        )

        if examples is None:
            print(f"No tuning examples provided, using up to {num_examples} training examples")
            examples = self.train_data
            if len(examples) > num_examples:
                examples = examples.sample(num_examples)
            examples = examples['text'].tolist()
        examples = [self.tokenizer(x) for x in examples]

        default_gptq_config = {
            'bits': 4, 
            'group_size': 128,
            'desc_act': False,
        }
        if gptq_config is None:
            print(f"No gptq_config provided, using default: {default_gptq_config}")
            gptq_config = default_gptq_config

        gptq_config = BaseQuantizeConfig(**gptq_config)
    
        model = AutoGPTQForCausalLM.from_pretrained(
            merged_name, 
            gptq_config,
            torch_dtype=torch.float16,
        )

        print("Quantizing model, this can take a while")
        model.quantize(examples)

        if quantized_model_path.exists():
            shutil.rmtree(quantized_model_path)
        quantized_model_path.mkdir(exist_ok=True, parents=True)

        self.tokenizer.save_pretrained(quantized_model_path)
        model.save_quantized(quantized_model_path, use_safetensors=True)
        model.config.save_pretrained(quantized_model_path)

        if push:
            self.push_quantized_model(quantized_model_path, quantized_name)