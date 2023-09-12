from copy import deepcopy
from instructor import OpenAISchema
import openai
import requests
import simplejson as json
from docketanalyzer.utils import OPENAI_API_KEY


class SimpleInstructor(OpenAISchema):
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

