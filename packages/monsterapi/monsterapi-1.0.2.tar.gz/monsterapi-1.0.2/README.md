# Monsterapi v2

A Python client for interacting with Monster API v2 in .

## Installation

```bash
pip install monsterapi
```

Has support to following MonsterAPI services:

Available models:
-----------------

Text-Gen/LLMs:
---------------

    1. falcon-7b-instruct
    2. mpt-7b-instruct
    3. llama2-7b-chat
    4. falcon-40b-instruct
    5. mpt-30b-instruct

**Others models are accessible through client but are not activated yet. Will be updated shortly.**

Image Gen:
----------

    1. txt2img - stable-diffusion v1.5
    2. sdxl - stable-diffusion XL V1.0
    3. pix2pix -  Instruct-pix2pix
    4. img2img - Image to Image using Stable Diffusion

Speech Gen:
-----------

    1. sunoai-bark - Bark (Sunoai Bark)
    2. whisper -  (Whisper Large V2)
    
## Usage

### Import Module

```python
from monsterapi import client
```

### set `MONSTER_API_KEY` env variable to your API key.

```bash
os.environ["MONSTER_API_KEY"] = <your_api_key>
client = client() # Initialize client
```

or

### pass `api_key` parameter to client constructor.

```bash
client = client(<api_key>) # pass api_key as parameter
```


### Send a response to a model and suitable payload and retreive payload
```python
# Fetching a response
response = client.get_response(model='falcon-7b-instruct', data={
    "prompt": "Your prompt here",
    # ... other parameters
})
print(response["process_id"])
```
### Get the status of the process
```python
status = client.get_status("your_process_id")
print(status)
```

### Wait and Get the Result
```python
# Waiting for result
result = client.wait_and_get_result("your_process_id")
print(result)
```
or 

### Use generate method
```python
result = client.generate(model='falcon-7b-instruct', data={
    "prompt": "Your prompt here",
    # ... other parameters
})
```

*Note: Input Model Payload Parameters can be found [here](./docs/InputModelPayload.md)*

## Run tests

### Install test dependencies

```bash
pip install monsterapi[tests]
```

### Run functional tests involving actual API key

```bash
export MONSTER_API_KEY=<your_api_key>
python3 -m pytest tests/ # Run all tests includes functional tests using actual API key
```

### Run unit tests

```bash
export MONSTER_API_KEY="dummy"
python3 -m pytest tests/ -m "not slow" # Run only unit tests
```

## PIP package push Instructions

```
pip install --upgrade setuptools wheel

python setup.py sdist bdist_wheel

pip install twine

twine upload dist/*
```

# About us

Check us out at [monsterapi.ai](https://monsterapi.ai)

Check out new no-code finetuning service [here](https://docs.monsterapi.ai/fine-tune-a-large-language-model-llm/launch-a-fine-tuning-job)

Checkout our Monster-SD Stable Diffusion v1.5 vs XL Comparison space [here](https://huggingface.co/spaces/qblocks/Monster-SD)

Checkout our Monster API LLM comparison space [here](https://huggingface.co/spaces/qblocks/Monster-LLMs)
