from copy import deepcopy
from instructor import OpenAISchema, MultiTask
from pydantic import BaseModel, create_model
import openai
import requests


class SimpleOpenAISchema(OpenAISchema):
    @classmethod
    def call(cls, inputs, model='gpt-4', max_tokens=512, temperature=0, **kwargs):
        r = openai.ChatCompletion.create(
            messages=cls.process_inputs(inputs),
            functions=[cls.openai_schema],
            function_call={"name": cls.openai_schema["name"]},
            model=model, max_tokens=max_tokens, temperature=temperature,
            **kwargs,
        )
        obj = cls.from_response(r)
        return cls.process_outputs(obj)

    @staticmethod
    def process_inputs(inputs):
        """Convert inputs into OpenAI message object, override to customize"""
        return [{
            'role': 'user', 
            'content': inputs
        }]

    @staticmethod
    def process_outputs(obj):
        """Override to customize function call outputs"""
        return obj.model_dump()


def SimpleMultiTask(cls):
    task_name = cls.__name__
    name = f"Multi{task_name}"
    multi_cls = MultiTask(cls)
    return create_model(name, __base__=(multi_cls, SimpleOpenAISchema))

