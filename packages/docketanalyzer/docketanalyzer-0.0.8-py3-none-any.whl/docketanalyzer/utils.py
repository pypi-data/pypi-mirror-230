import os
from dotenv import load_dotenv
import openai
from pathlib import Path
import simplejson as json


load_dotenv()


OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
RUNPOD_API_KEY = os.environ.get('RUNPOD_API_KEY')
RUNPOD_INFERENCE_ENDPOINT_ID = os.environ.get('RUNPOD_INFERENCE_ENDPOINT_ID')

openai.api_key = OPENAI_API_KEY


AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', None)
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', None)
AWS_S3_ENDPOINT_URL = os.environ.get('AWS_S3_ENDPOINT_URL', None)
AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', None)
AWS_S3_BUCKET_NAME = os.environ.get('AWS_S3_BUCKET_NAME', None)

