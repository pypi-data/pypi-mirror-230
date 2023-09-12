import os
from dotenv import load_dotenv
from pathlib import Path
import simplejson as json


load_dotenv()


RUNPOD_API_KEY = os.environ.get('RUNPOD_API_KEY')

