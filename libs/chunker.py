#encoding=utf-8
import asyncio
import json
import random
import datetime

from libs import embedder
import logger
# from libs.CABLY import chat_completion, ChatHistory, ChatRole, ChatModels, ChatMessage


# models_priority = [ChatModels.ClaudeHaiku, ChatModels.GPT4o, ChatModels.GPT35Turbo]
from AIIO import askBetterLLM, LLMCallPriority
async def split_to_chunks(context_payload:list):
    system_prompt = '''Разбей сообщение пользователя на чанки.
Чанк - это сокращённое описание 1 логически отдельной части. Он занимает ОДНУ строку и не имеет разметки
Полезная информация - информация, которая может пригодиться в долгосрочной перспективе в качестве воспоминания. Бесполезную информацию игнорируй
Пользователь, вероятно, разметил в * действие.
В ответе дай ТОЛЬКО чанки. 1 строка = 1 чанк.
Если несколько чанков логически связаны и несут мало полезной информации - склей их и отсей лишнее.
ТОЛЬКО перед ОСОБО важными чанками добавь [!] - по этим чанкам будет поиск в памяти. Таких чанков не должно быть много лили может не быть вовсе
Ориентируйся на пользу чанков в будущем - они будут подгружены только как воспоминания о прошлом. это так же значит, что в чанке должен быть контекст.
Для контекста тебе дана часть истории, однако она уже обработана. Твоя цель только последнее сообщение пользователя.'''
    # messages = ChatHistory([ChatMessage(ChatRole.System, system_prompt), ChatMessage(ChatRole.User, text)])
    # resp = None
    # for model in models_priority:
    #     resp = await chat_completion(messages, model)
    #     # print(f"Model {model} used {resp.usage.total_tokens} tokens")
    #     await logger.log(f"EMBEDDING: Model {model} used {resp.usage.total_tokens} tokens")
    #     if resp.usage.total_tokens > 2:
    #
    #         break
    # else:
    #     return None

    # return resp.choices[0].message.content.split('\n')
    print(context_payload)
    payload = context_payload.copy()
    if payload[0]['role'] == 'system':
        payload.pop(0)
    payload.insert(0, {
        "role": "system",
        "content": system_prompt
    })
    print(payload)
    response = await askBetterLLM(payload, priority=LLMCallPriority.Speed)
    return response['result'].split('\n')


async def text_to_chunks_embedding(text):
    chunks = await split_to_chunks(text)
    embeddings = []
    for chunk in chunks:
        embeddings.append(embedder.get_embedding(chunk))
    return chunks, embeddings
