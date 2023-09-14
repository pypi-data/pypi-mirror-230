#MonsterAPIClient.py

"""
Monster API Python client to connect to LLM models on monsterapi

Base URL: https://api.monsterapi.ai/v1/generate/{model}

Available models:
-----------------

LLMs:
    1. falcon-7b-instruct
    2. falcon-40b-instruct
    3. mpt-30B-instruct
    4. mpt-7b-instruct
    5. openllama-13b-base
    6. llama2-7b-chat

Text to Image:
    1. stable-diffusion v1.5
    2. stable-diffusion XL V1.0

"""
import os
import time
import json
import logging
import requests
import mimetypes
from requests_toolbelt.multipart.encoder import MultipartEncoder

from typing import Optional, Literal, Union, List, Dict
from pydantic import BaseModel, Field

from monsterapi.InputDataModels import LLMInputModel1, LLMInputModel2, SDInputModel, MODELS_TO_DATAMODEL, FileField

# Use LOGGING_LEVEL environment variable to set logging level
# Default logging level is INFO
level = os.environ.get('LOGGING_LEVEL', 'INFO')

if level == 'DEBUG':
    logging.basicConfig(level=logging.DEBUG)
elif level == 'INFO':
    logging.basicConfig(level=logging.INFO)
elif level == 'WARNING':
    logging.basicConfig(level=logging.WARNING)
elif level == 'ERROR':
    logging.basicConfig(level=logging.ERROR)
elif level == 'CRITICAL':
    logging.basicConfig(level=logging.CRITICAL)

logger = logging.getLogger(__name__)


class MClient():
    def __init__(self, api_key: Optional[str] = None, base_url: str = 'https://api.monsterapi.ai/v1'):
        self.boundary = '---011000010111000001101001'
        
        if api_key is not None:
            self.auth_token = api_key
        else:
            self.auth_token = os.environ.get('MONSTER_API_KEY')
            if not self.auth_token:
                raise ValueError("MONSTER_API_KEY environment variable not set!")
        
        self.headers = {
            "accept": "application/json",
            'Authorization': 'Bearer ' + self.auth_token}
        self.base_url = base_url
        self.models_to_data_model = MODELS_TO_DATAMODEL
        

    def get_response(self, model, data: dict):
        if model not in self.models_to_data_model:
            raise ValueError(f"Invalid model: {model}!")

        dataModel = self.models_to_data_model[model](**data)
        
        form_data = {}
        files = {}
        
        # Convert model data to dictionary
        for key, value in dataModel.dict().items():
            form_data[key] = str(value)

        # Check for file fields
        for key, value in dataModel.__annotations__.items():
            if value == FileField:
                field_value = dataModel.__getattribute__(key)
                if not field_value.startswith('http'):
                    if os.path.exists(field_value):
                        file_type, _ = mimetypes.guess_type(field_value)
                        files[key] = (field_value, file_type)
                    else:
                        raise FileNotFoundError(f"File {field_value} not found!")
        
        # Combine form_data and files into a single dictionary
        for key, (file_path, file_type) in files.items():
            file_data = open(file_path, 'rb')
            # if size of file_data is greater than 8MB then raise error
            if os.path.getsize(file_path) > 8 * 1024 * 1024:
                raise ValueError(f"File size of {file_path} is greater than 8MB, currently not supported!")
            form_data[key] = (os.path.basename(file_path), file_data, file_type)
        
        multipart_encoder = MultipartEncoder(
            fields=form_data,
            boundary=self.boundary
        )
        
        headers = self.headers.copy()
        headers['Content-Type'] = f"multipart/form-data; boundary={self.boundary}"

        url = f"{self.base_url}/generate/{model}"

        response = requests.post(
            url,
            headers=headers,
            data=multipart_encoder
        )
        
        response.raise_for_status()
        return response.json()
    
    def get_status(self, process_id):
        # /v1/status/{process_id}
        url = f"{self.base_url}/status/{process_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def wait_and_get_result(self, process_id, timeout=100):
        start_time = time.time()
        while True:
            elapsed_time = time.time() - start_time

            if elapsed_time >= timeout:
                raise TimeoutError(f"Process {process_id} timed out after {timeout} seconds.")

            status = self.get_status(process_id)
            if status['status'].lower() == 'completed':
                return status['result']
            elif status['status'].lower() == 'failed':
                raise RuntimeError(f"Process {process_id} failed! {status}")
            else:
                logger.debug(f"Process {process_id} is still running, status is {status['status']}. Waiting ...")
                time.sleep(0.01)

    def generate(self, model, data: dict):
        response = self.get_response(model, data)
        process_id = response['process_id']
        return self.wait_and_get_result(process_id)
