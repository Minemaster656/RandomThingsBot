import g4f

import utils
import json
import time

import requests
from private import coreData

g4f.logging = True  # enable logging
g4f.check_version = False  # Disable automatic version checking
print(g4f.version)  # check version
print(g4f.Provider.Ails.params)  # supported args


# Automatic selection of provider

# streamed completion

# response = g4f.ChatCompletion.create(
#     model="gpt-3.5-turbo",
#     messages=[{"role": "user", "content": "Hello"}],
#     stream=True,
# )
#
# for message in response:
#     print(message, flush=True, end='')

# # normal response
# response = g4f.ChatCompletion.create(
#     model=g4f.models.gpt_4,
#     messages=[{"role": "user", "content": "Hello"}],
# )  # alternative model setting
#
# print(response)
async def askGPT(system_prompt: str, user_prompt: str, useGPT4: bool):
    messages = []
    if not utils.checkStringForNoContent(system_prompt):
        messages.append({{"role": "system", "content": f"{system_prompt}"}})
    messages.append({"role": "user", "content": f"{user_prompt}"})
    # normal response
    response = g4f.ChatCompletion.create(
        model=g4f.models.gpt_4 if useGPT4 else "gpt-3.5-turbo",
        messages=messages,
    )  # alternative model setting

    return response


class Text2ImageAPI:

    def __init__(self, url, api_key, secret_key):
        self.URL = url
        self.keys = coreData.API_KEYS["kandinskiy3"]

        self.AUTH_HEADERS = {
            'X-Key': f'Key {self.keys["public"]}',

            'X-Secret': f'Secret {self.keys["secret"]}',
        }

    def get_model(self):
        response = requests.get(self.URL + 'key/api/v1/models', headers=self.AUTH_HEADERS)
        data = response.json()
        return data[0]['id']

    def generate(self, prompt, model, images=1, width=1024, height=1024):
        params = {
            "type": "GENERATE",
            "numImages": images,
            "width": width,
            "height": height,
            "generateParams": {
                "query": f"{prompt}"
            }
        }

        data = {
            'model_id': (None, model),
            'params': (None, json.dumps(params), 'application/json')
        }
        response = requests.post(self.URL + 'key/api/v1/text2image/run', headers=self.AUTH_HEADERS, files=data)
        data = response.json()
        return data['uuid']

    def check_generation(self, request_id, attempts=10, delay=10):
        while attempts > 0:
            response = requests.get(self.URL + 'key/api/v1/text2image/status/' + request_id, headers=self.AUTH_HEADERS)
            data = response.json()
            if data['status'] == 'DONE':
                return data['images']

            attempts -= 1
            time.sleep(delay)


if __name__ == '__main__':
    api = Text2ImageAPI('https://api-key.fusionbrain.ai/', 'YOUR_API_KEY', 'YOUR_SECRET_KEY')
    model_id = api.get_model()
    uuid = api.generate("Sun in sky", model_id)
    images = api.check_generation(uuid)
    print(images)

# Не забудьте указать именно ваш YOUR_KEY и YOUR_SECRET.
