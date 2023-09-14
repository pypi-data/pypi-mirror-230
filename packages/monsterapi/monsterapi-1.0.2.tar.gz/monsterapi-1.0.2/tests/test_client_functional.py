import os
import shutil
import pytest
import requests
import tempfile
import unittest
from random import randint
from monsterapi import client
from monsterapi.InputDataModels import LLMInputModel1, LLMInputModel2, SDInputModel, MODELS_TO_DATAMODEL, Img2Img, Pix2Pix, Txt2Speech,Speech2Txt 

enabled_models = ["whisper", "falcon-7b-instruct", "llama2-7b-chat", "mpt-7b-instruct", "sdxl-base", "txt2img", "sunoai-bark"]

temp_dir = tempfile.TemporaryDirectory()

class TestMClientFunctional(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = client()
        pre_download_files = [
            'https://i.pinimg.com/originals/1c/31/8e/1c318ed6a76b5c1573f0f816516beea3.jpg',
            'https://img.freepik.com/free-photo/young-curly-man-with-thumbs-up-isolated-blue-wall_231208-1245.jpg',
            'https://upload.wikimedia.org/wikipedia/commons/2/23/Rickard_Falkvinge_interview_after_demonstration_2007-06-07.ogg'

        ]

        temp_dir_name = temp_dir.name

        local_file_names = [os.path.join(temp_dir_name, os.path.basename(i)) for i in pre_download_files]

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.3'}

        # download files into tempdir
        for url, local_file_name in zip(pre_download_files, local_file_names):
            # Download the file
            response = requests.get(url, headers=headers, stream=True)
            response.raise_for_status()  
            with open(local_file_name, 'wb') as f:
                shutil.copyfileobj(response.raw, f)
            if not os.path.exists(local_file_name):
                raise Exception(f"Failed to download file {url} into {local_file_name}")

        cls.sample_data = {
            LLMInputModel1: [{"prompt": "Write an essay on Mars",
                             "top_k":40,"top_p":0.8,"max_length":256,"repitition_penalty":1.2,
                             "beam_size":1}],

            LLMInputModel2: [{"prompt": "Write an essay on Earth", "top_k":40,"top_p":0.8,"temp" : 0.9,"max_length":256}],

            SDInputModel: [{"prompt": "Sunset over a mountain range","steps":50,"samples":2,"aspect_ratio":"square","guidance_scale":7.5}],

            Img2Img: [
                        {   "init_image_url": "https://i.pinimg.com/originals/1c/31/8e/1c318ed6a76b5c1573f0f816516beea3.jpg",
                          "prompt": "A fantasy landscape, beautiful, photorealistic, trending on artstation",
                          "steps":30,
                          "strength":0.75,
                          "guidance_scale":7.5
                          },
                        {   "init_image_url": local_file_names[0],
                          "prompt": "A fantasy landscape, beautiful, photorealistic, trending on artstation",
                          "steps":30,
                          "strength":0.75,
                          "guidance_scale":7.5
                          },

                    ],

            Pix2Pix:  [
                        {   "init_image_url": "https://img.freepik.com/free-photo/young-curly-man-with-thumbs-up-isolated-blue-wall_231208-1245.jpg",
                          "prompt": "Add mountains in background","steps":30,
                          "guidance_scale":7.5,
                          "image_guidance_scale":1.5
                          },
                        {   "init_image_url": local_file_names[1],
                          "prompt": "Add mountains in background","steps":30,
                          "guidance_scale":7.5,
                          "image_guidance_scale":1.5
                          },
                        ],

            Txt2Speech: [{"prompt": "What's the meaning of life?","speaker":"en_speaker_4",
                         "sample_rate":25000,
                         "text_temp":0.5,"waveform_temp":0.5}],

            Speech2Txt: [
                {
                    "file": "https://upload.wikimedia.org/wikipedia/commons/2/2d/A_J_Cook_Speech_from_Lansbury%27s_Labour_Weekly.ogg",
                    "transcription_format":"srt","language":'en'
                    },
                {
                    "file": local_file_names[2],
                    "transcription_format":"srt","language":'en'
                    },
                ]
        }

    @classmethod
    def create_test_function(cls, model_name, data_model):
        def test_func(self):
            if model_name in enabled_models:
                input_data_list = self.sample_data[data_model]
                for input_data in input_data_list:
                    response = self.client.get_response(model_name, input_data)

                    self.assertIn("process_id", response)
                    process_id = response["process_id"]

                    # Check status
                    status_response = self.client.get_status(process_id)
                    self.assertIn("status", status_response)
                    if status_response["status"] == "FAILED":
                        self.fail(f"Failed to get response for model {model_name} with process id {process_id}.")

                    # If not failed, wait and get result
                    result_response = self.client.wait_and_get_result(process_id, timeout=60)
                
                    if data_model == SDInputModel or data_model== Txt2Speech:
                        self.assertIn("output", result_response)
                    else:
                        self.assertIn("text", result_response)
            else:
                pytest.skip(f"Skipping test for model {model_name} as it is not enabled.")
        return test_func

# Dynamically add test methods
for model, data_model in MODELS_TO_DATAMODEL.items():
    target_function = TestMClientFunctional.create_test_function(model, data_model)
    test_name = f"test_{model}_functionally"
    setattr(TestMClientFunctional, test_name, target_function)

if __name__ == "__main__":
    unittest.main()
