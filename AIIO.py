'''Artificial Intelligence Input-Output:
Класс для запросов к API или локальным ИИ'''
import enum
import json
import time
import uuid

import aiohttp

from private import coreData as core

gigachat_temptoken = None


class LLMs(enum.Enum):
    '''Text generation Large Language Models'''
    ANY = 0
    GIGACHAT = 1
    YANDEXGPT = 2
    CHATGPT3 = 3
    CHATGPT4 = 4
    G4F = 5


class Text2Imgs(enum.Enum):
    '''Text prompt to image. Kandinsky supports русский язык'''
    ANY = 0
    KANDINSKY = 1
    DALLE3 = 2


async def askLLM(payload, model, payload_cutoff, temptoken=gigachat_temptoken):
    '''payload is {JSON} object:
    temptoken это AIIO.gigachat_temptoken
    структура payload диалога:
    [{"role":роль, "content":строка}, ...]
    роли::
    user - пользователь
    system - системный промпт
    assistant - ответ модели
    '''
    response = "Модель не ответила..."
    print(payload,"\n",
          model,"\n",
          payload_cutoff,"\n",
          temptoken,"\n")
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
                    print(response_text)
                    gigachat_temptoken = response_text
                    temptoken = gigachat_temptoken
                    print(headers, " ", data)
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
            "max_tokens": 512,
            "repetition_penalty": 1,
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
        print("-----")
        print(headers, "\n", data)
        print("-----")
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
            async with session.post(url, headers=headers, data=data) as resp:
                response_text = await resp.json()
                print(response_text)
                response = response_text['choices'][0]["message"]["content"]
    print(response)
    return response

