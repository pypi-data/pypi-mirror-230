import os
from dotenv import load_dotenv
from pathlib import Path
import simplejson as json


load_dotenv()


OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
RUNPOD_API_KEY = os.environ.get('RUNPOD_API_KEY')
RUNPOD_INFERENCE_ENDPOINT_ID = os.environ.get('RUNPOD_INFERENCE_ENDPOINT_ID')

