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
Не подписывай начало и конец чанков. Не оставляй только цитату в чанке!
Ориентируйся на пользу чанков в будущем - они будут подгружены только как воспоминания о прошлом. это так же значит, что в чанке должен быть контекст. Учти, что чанки будут использованы по отдельности и у каждого контекст должен быть независимо понятен.
Для контекста тебе дана часть истории, однако она уже обработана. Твоя цель только последнее сообщение пользователя. Перед ним добавлено несколько равно, с них начинается необработанное.'''
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
    if len(payload) >= 3:
        payload[-2]["content"] = "===== [SYSTEM_MARKER: UNPROCESSED DATA STARTS HERE] ====="+payload[-1]["content"]
    # await logger.log(str(payload), logger.LogLevel.DEBUG)
    response = await askBetterLLM(payload, priority=LLMCallPriority.Quality)
    # await logger.log(str(response['result']), logger.LogLevel.DEBUG)

    return response['result'].split('\n')


async def text_to_chunks_embedding(text):
    chunks = await split_to_chunks(text)
    embeddings = []
    for chunk in chunks:
        embeddings.append(embedder.get_embedding(chunk))
    return chunks, embeddings
