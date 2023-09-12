"""
Spin off from jxnl's gist:
https://x.com/jxnlco/status/1668903199426887680
https://gist.github.com/jxnl/72f1225b44f59522a834ea15543fa1f8
"""
from copy import deepcopy
from pydantic import BaseModel, Field
import requests
import simplejson as json
from docketanalyzer.utils import OPENAI_API_KEY


def chat_response(
    messages, functions=None, 
    model='gpt-4', 
    max_tokens=512, temperature=0,
    api_key=None, org_id=None,
):
    if api_key is None:
        api_key = OPENAI_API_KEY
    if api_key is None:
        raise ValueError('must pass api_key or set OPENAI_API_KEY environment variable')

    url = 'https://api.openai.com/v1/chat/completions'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    if org_id is not None:
        headers['OpenAI-Organization'] = org_id
    
    data = {
        'model': model,
        'messages': messages,
        'max_tokens': max_tokens,
        'temperature': temperature,
    }

    if functions is not None:
        data['functions'] = functions
        data['function_call'] = {
            "name": functions[0]['name']
        }
    response = requests.post(url, headers=headers, json=data)
    return response


def schema2function(parameters):
    """Convert a Pydantic schema to an OpenAI function"""
    schema = {}

    schema['name'] = parameters['title']
    del parameters['title']

    schema['description'] = parameters['description']
    del parameters['description']

    for k, v in parameters['properties'].items():
        if 'title' in v:
            del v['title']
        if 'items' in v:
            if '$ref' in v['items']:
                related_definition = v['items']['$ref'].split('/')[-1]
                related_schema = schema2function(parameters['definitions'][related_definition])
                v['items'] = related_schema

    if 'definitions' in parameters:
        del parameters['definitions']
    
    schema['parameters'] = parameters
    return schema


class BaseFunction(BaseModel):
    def __init__(
        self, text, model='gpt-4', 
        max_tokens=512, temperature=0, 
        rate_limit_retries=0, rate_limit_pause=15,
        api_key=None, org_id=None,
    ):
        messages = self.process_inputs(text)
        function = self.function()

        for i in range(rate_limit_retries + 1):
            r = chat_response(
                messages, functions=[function], 
                model=model, max_tokens=max_tokens, temperature=temperature,
                api_key=api_key, org_id=org_id,
            )
            if r.status_code == 429:
                print(f'Rate limit reached, pausing for {rate_limit_pause} seconds')
                time.sleep(rate_limit_pause)
            else:
                break

        r = r.json()
        kwargs = r['choices'][0]['message']['function_call']['arguments']
        kwargs = json.loads(kwargs)
        super().__init__(**kwargs)

    @classmethod
    def function(cls):
        schema = schema2function(deepcopy(cls.model_json_schema()))
        return schema

    def process_inputs(self, text):
        """Convert inputs into OpenAI message object, override to customize"""
        return [{
            'role': 'user', 
            'content': text
        }]

    def apply(self):
        """Override to customize function call outputs"""
        return self.model_dump()


class truth_checker(BaseFunction):
    """
    We're looking for the Truth!
    """

    is_true: bool = Field(..., description=("Is this true?"))

    def apply(self):
        if self.is_true:
            return 'This is true!'
        else:
            return 'This is false!'


x = truth_checker('The sky is blue.')
print(x.apply())

