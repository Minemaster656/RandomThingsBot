'''Artificial Intelligence Input-Output:
Класс для запросов к API или локальным ИИ'''
import asyncio
import base64
import enum
import io
import json
import random
import time
import uuid

import aiohttp
import discord
import requests
from openai import AsyncOpenAI

import graphics.BASE64
import private.coreData
from private import coreData as core

from factcheckexplorer.factcheckexplorer import FactCheckLib

gigachat_temptoken = None

openai = AsyncOpenAI(
    api_key=private.coreData.API_KEYS["deepinfra"],
    base_url="https://api.deepinfra.com/v1/openai",
)


class LLMs(enum.Enum):
    '''Text generation Large Language Models'''
    ANY = 0
    GIGACHAT = 1
    YANDEXGPT = 2
    CHATGPT3 = 3
    CHATGPT4 = 4
    G4F = 5
    MISTRALAI = 6
    MIXTRAL7X8 = 7


class Text2Imgs(enum.Enum):
    '''Text prompt to image. Kandinsky supports русский язык'''
    ANY = 0
    KANDINSKY = 1
    DALLE3 = 2


class KandinskyStyles(enum.Enum):
    DEFAULT = 0


async def askLLM(payload, model: LLMs, payload_cutoff, temptoken=gigachat_temptoken, max_tokens=512):
    '''payload is {JSON} object:
    temptoken это AIIO.gigachat_temptoken
    структура payload диалога:
    [{"role":роль, "content":строка}, ...]
    роли::
    user - пользователь
    system - системный промпт
    assistant - ответ модели
    '''
    tokens = {"prompt_tokens": 0,
              "completion_tokens": 0,
              "total_tokens": 0,
              "system_tokens": 0
              }
    response = "Модель не ответила..."
    # print(payload, "\n",
    #       model, "\n",
    #       payload_cutoff, "\n",
    #       temptoken, "\n")
    if model == LLMs.GIGACHAT:
        async def makeTemptoken():
            global gigachat_temptoken
            url = 'https://ngw.devices.sberbank.ru:9443/api/v2/oauth'
            headers = {'Authorization': "Basic " + core.API_KEYS["GigaChat"]["auth"], 'RqUID': f'{uuid.uuid4()}',
                       'Content-Type': 'application/x-www-form-urlencoded'}
            data = 'scope=GIGACHAT_API_PERS'  # данные, которые вы хотите отправить

            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
                async with session.post(url, headers=headers, data=data) as response:
                    response_text = await response.json()
                    # print(response_text)
                    gigachat_temptoken = response_text
                    temptoken = gigachat_temptoken
                    # print(headers, " ", data)

        if temptoken is None:
            await makeTemptoken()
            temptoken = gigachat_temptoken
            # return "No token"
        if temptoken["expires_at"] < time.time() * 1000 - (60000):
            await makeTemptoken()
            temptoken = gigachat_temptoken
            # return "No token"

        url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {temptoken["access_token"]}'

        }
        data = {
            'model': "GigaChat",
            "messages": payload,
            "temperature": 1,
            "top_p": 0.1,
            "n": 1,
            "stream": False,
            "max_tokens": max_tokens,
            "repetition_penalty": 1.15,
            "update_interval": 0

        }
        data = json.dumps(data)
        # r = {
        #     "choices": [
        #         {
        #             "message": {
        #                 "content": "Привет! К сожалению, я не могу предоставить точную дату выпуска GigaChat, так как это зависит от многих факторов, включая завершение разработки, тестирование и получение необходимых разрешений. Однако, я могу сказать, что мы прилагаем все усилия, чтобы сделать GigaChat максимально полезной и безопасной для пользователей.",
        #                 "role": "assistant"
        #             },
        #             "index": 0,
        #             "finish_reason": "stop"
        #         }
        #     ],
        #     "created": 1707583886,
        #     "model": "GigaChat:3.1.24.3",
        #     "object": "chat.completion",
        #     "usage": {
        #         "prompt_tokens": 230,
        #         "completion_tokens": 71,
        #         "total_tokens": 301,
        #         "system_tokens": 0
        #     }
        # }
        # print("-----")
        # print(headers, "\n", data)
        # print("-----")
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
            async with session.post(url, headers=headers, data=data) as resp:
                response_text = await resp.json()
                # print(response_text)
                # print(response_text)
                response = response_text['choices'][0]["message"]["content"]
                tokens = response_text['usage']
    # print(response)

    return (response, tokens)


class Text2ImageAPI:

    def __init__(self, url, api_key, secret_key):
        self.URL = url
        self.AUTH_HEADERS = {
            'X-Key': f'Key {api_key}',
            'X-Secret': f'Secret {secret_key}',
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


async def askT2I(prompt: str, model: Text2Imgs,
                 negative_prompt: str = "Кислотные оттенки, смазанная картинка, искажённые пропорции",
                 sizeX: int = 1024, sizeY: int = 1024,
                 style: KandinskyStyles = KandinskyStyles.DEFAULT, token_index=0, images_count=1):
    '''output = {
        "code": 200,
        "censored": False,
        "image": "base64 string"
    }'''
    tasks = []
    output_array = []
    # print(prompt)
    async def callAPI(token_index):
        output = {
            "code": 200,
            "censored": False,
            "image": ""
        }
        # print("Building headers...")
        headers = {
            'X-Key': f'Key {core.API_KEYS["kandinskiy3"][token_index]["X-Key"]}',
            'X-Secret': f'Secret {core.API_KEYS["kandinskiy3"][token_index]["X-Secret"]}',
        }
        # print("Headers build complete...")
        params = {
            "type": "GENERATE",
            "numImages": 1,
            "width": sizeX,
            "height": sizeY,
            "negativePromptUnclip": f"{negative_prompt}",
            "generateParams": {
                "query": f"{prompt}",

            }
        }

        # data = {
        #
        #     "type": "GENERATE",
        #     "style": "DEFAULT",
        #     "width": sizeX,
        #     "height": sizeY,
        #     "num_images": 1,
        #     "negativePromptUnclip": f"{negative_prompt}",
        #     "generateParams": {
        #         "query": f"{prompt}",
        #     }
        #
        # }

        def get_model():
            response = requests.get("https://api-key.fusionbrain.ai/" + 'key/api/v1/models', headers=headers)
            data = response.json()
            return data[0]['id']

        # data = json.dumps(data)
        data = {
            'model_id': (None, get_model),
            'params': (None, json.dumps(params), 'application/json')
        }

        # data = aiohttp.FormData()
        # data.add_field('model_id', '1')
        # data.add_field('params', json.dumps(params))
        files = aiohttp.FormData()
        files.add_field(name='params', value=json.dumps(params), content_type='application/json')
        files.add_field(name='model_id', value=str(get_model()))

        # print("Data: ", data)
        url = "https://api-key.fusionbrain.ai/" + "key/api/v1/text2image/run"
        # print("URL: ", url)
        #
        # print(isinstance(data, dict))
        uuid = ""
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
            async with session.post(url, headers=headers, data=files) as response:
                response_json = await response.json()
                # {
                #     "uuid": "string",
                #     "status": "string",
                #     "images": ["string"],
                #     "errorDescription": "string",
                #     "censored": "false"
                # }
                if "uuid" in response_json.keys():
                    uuid = response_json["uuid"]
                else:
                    uuid = "NSFW"

                # print(response_json)

        async def check_generation(request_id, attempts=10, delay=15):
            while attempts > 0:
                response = requests.get("https://api-key.fusionbrain.ai/" + 'key/api/v1/text2image/status/' + request_id,
                                        headers=headers)
                data = response.json()

                if data['status'] == 'DONE':
                    output["censored"] = data["censored"]
                    return data['images'][0]

                attempts -= 1
                await asyncio.sleep(delay)
            return "Error"

        # if uuid != "NSFW":
        gen = await check_generation(uuid)

        # else:
        #     gen ="NSFW"

        # output['censored'] = response_json['censored']
        output['image'] = gen
        output_array.append(output)

    for i in range(images_count):
        task = callAPI(i)
        tasks.append(task)


    await asyncio.gather(*tasks)

    return output_array


def kandinskyOutputToFile(gen):
    if gen['image']:
        if gen['image'] == "Error":
            file_content = io.BytesIO(base64.b64decode(graphics.BASE64.error))
        elif gen['censored'] == True:
            file_content = io.BytesIO(base64.b64decode(graphics.BASE64.nsfw))
        else:
            file_content = io.BytesIO(base64.b64decode(gen["image"]))

        file = discord.File(filename=f"gen_kandinsky_{random.randint(0, 35565)}.png", fp=file_content)
        return file
    else:
        return None


async def askBetterLLM(payload: list, max_tokens=512):
    '''payload structure:
        [{"role": "system", "content": "Hello world"},
        {"role": "user", "content": "Hello world"},
        {"role": "assistant", "content": "Hello world"}
        ]

    output:
        {"result":result, "output":payload, "total_tokens":total_tokens, "factcheck":factcheck}
    '''

    result = "Something went terribly wrong."
    fail = False
    tokens = 0
    total_tokens = 0
    try:
        chat_completion = await openai.chat.completions.create(
            model = "mistralai/Mistral-7B-Instruct-v0.3",
            # model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            # model="mistralai/Mistral-7B-Instruct-v0.1",
            # model="openchat/openchat_3.5",
            messages=payload,
            max_tokens=max_tokens,
        )
        # print(chat_completion)
        result = chat_completion.choices[0].message.content
        total_tokens = chat_completion.usage.total_tokens
        # total_tokens = chat_completion.total_tokens

    except Exception as e:
        # print(e)
        fail = True

    payload.append({"role": "assistant", "content": result})
    if fail:
        payload = payload[:-2]



    # fact_check = FactCheckLib(query=result, language="ru", num_results=200)
    #
    # rjson = fact_check.fetch_data()
    # data = fact_check.clean_json(rjson)
    # edata = fact_check.extract_info(data)

    return {"result": result, "output": payload, "prompt_tokens": tokens, "total_tokens": total_tokens}

