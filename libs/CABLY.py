from typing import Union

import aiohttp
import asyncio
import os
from enum import Enum
import json


from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('CABLY_AI_TOKEN')

class ChatModels(Enum):
    ClaudeHaiku = "claude-3-5-haiku-20241022"
    Cably80B = "Cably-80B"
    AnyUncensored = "any-uncensored"
    GPT4oMini = "gpt-4o-mini" #FREE
    GPT35Turbo = "gpt-3.5-turbo"
    CommandLight = "command-light"
    CommandNightly = "command-nightly"
    GPT4o = "chatgpt-4o-latest"
    SearchGPT = "searchgpt"
    ClaudeSonnet = "claude-3-sonnet"
    DeepseekR1 = "deepseek-r1" #FREE
    AionRP = "aion-rp"

class Text2ImgModels(Enum):
    Dalle2 = "dall-e-2"
    Dalle3 = "dall-e-3"
    Flux = "flux"
    FluxAnime = "flux-anime"
    FluxDisney = "flux-disney"
    FluxPixel = "flux-pixel"
    Flux3D = "flux-3d"
    FluxRealism = "flux-realism"
    FLUX1Dev = "FLUX.1 [dev]"
    FLUX1Pro = "FLUX.1 [pro]"
    FLUX1Schnell = "FLUX.1 [schnell]"
    FLUX1_1ProUltraRaw = "FLUX 1.1 [pro] ultra raw"
    Grok2Aurora = "grok-2-aurora"
    IdeogramV2Turbo = "ideogram-v2-turbo"
    Imagen30FastGenerate001 = "imagen-3.0-fast-generate-001"
    Imagen30Generate001 = "imagen-3.0-generate-001"
    PlaygroundV25 = "playground-v2.5"
    PlaygroundV3 = "playground-v3"
    RecraftV3 = "recraft-v3"
    SD3_5 = "sd3.5"
    SDXLLightning4Step = "sdxl-lightning-4step"
    StableDiffusion3 = "stable-diffusion-3"
    StableDiffusion3LargeTurbo = "stable-diffusion-3-large-turbo"
    StableDiffusion35Large = "stable-diffusion-3.5-large"
    StableDiffusion35Turbo = "stable-diffusion-3.5-turbo"
    StableDiffusionUltra = "stable-diffusion-ultra"
    StableDiffusionV15 = "stable-diffusion-v1.5"

# class ImageGenerationModels(Enum):
#     SDV1Inpainting = "sd-v1-inpainting"
#     SuperResolution = "super-resolution"

class AudioSpeechModels(Enum):
    Jeff = "jeff"
    Alloy = "alloy"

class AudioTranscriptionModels(Enum):
    WhisperAdvanced = "whisper-advanced"

class ModerationModels(Enum):
    TextModerationLatest = "text-moderation-latest"
    OmniModerationLatest = "omni-moderation-latest"
    TextModerationStable = "text-moderation-stable"


#! MODERATION

async def moderate_raw(text: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.post(
            'https://cablyai.com/v1/moderations',
            headers={
                'accept': 'application/json',
                'Authorization': f'Bearer {API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                "input": text,
                "model": "text-moderation-latest"
            }
        ) as response:
            return await response.json()

     
class ModerationResponse:
    def __init__(self, id: str, model: str, results: list):
        self.id = id
        self.model = model
        self.results = results
    def get_true_categories(self) -> dict:
        return extract_true_moderation_categories(self.results[0].categories)

class ModerationResult:
    def __init__(self, flagged: bool, categories: dict, category_scores: dict):
        self.flagged = flagged
        self.categories = categories
        self.category_scores = category_scores

class Categories:
    def __init__(self, sexual: bool, hate: bool, harassment: bool, self_harm: bool,
                    sexual_minors: bool, hate_threatening: bool, violence_graphic: bool,
                    self_harm_intent: bool, self_harm_instructions: bool,
                    harassment_threatening: bool, violence: bool):
        self.sexual = sexual
        self.hate = hate
        self.harassment = harassment
        self.self_harm = self_harm
        self.sexual_minors = sexual_minors
        self.hate_threatening = hate_threatening
        self.violence_graphic = violence_graphic
        self.self_harm_intent = self_harm_intent
        self.self_harm_instructions = self_harm_instructions
        self.harassment_threatening = harassment_threatening
        self.violence = violence

class CategoryScores:
    def __init__(self, sexual: float, hate: float, harassment: float, self_harm: float,
                    sexual_minors: float, hate_threatening: float, violence_graphic: float,
                    self_harm_intent: float, self_harm_instructions: float,
                    harassment_threatening: float, violence: float):
        self.sexual = sexual
        self.hate = hate
        self.harassment = harassment
        self.self_harm = self_harm
        self.sexual_minors = sexual_minors
        self.hate_threatening = hate_threatening
        self.violence_graphic = violence_graphic
        self.self_harm_intent = self_harm_intent
        self.self_harm_instructions = self_harm_instructions
        self.harassment_threatening = harassment_threatening
        self.violence = violence
def extract_true_moderation_categories(categories: Categories) -> dict:
    true_categories = {
        "sexual": categories.sexual,
        "hate": categories.hate,
        "harassment": categories.harassment,
        "self_harm": categories.self_harm,
        "sexual_minors": categories.sexual_minors,
        "hate_threatening": categories.hate_threatening,
        "violence_graphic": categories.violence_graphic,
        "self_harm_intent": categories.self_harm_intent,
        "self_harm_instructions": categories.self_harm_instructions,
        "harassment_threatening": categories.harassment_threatening,
        "violence": categories.violence
    }
    
    # Удаляем категории, которые имеют значение False
    true_categories = {k: v for k, v in true_categories.items() if v}
    return true_categories if true_categories else None
def moderation_json_to_class(json_response: dict) -> ModerationResponse:
    results = []
    for result in json_response.get("results", []):
        categories = Categories(
            sexual=result["categories"].get("sexual", False),
            hate=result["categories"].get("hate", False),
            harassment=result["categories"].get("harassment", False),
            self_harm=result["categories"].get("self-harm", False),
            sexual_minors=result["categories"].get("sexual/minors", False),
            hate_threatening=result["categories"].get("hate/threatening", False),
            violence_graphic=result["categories"].get("violence/graphic", False),
            self_harm_intent=result["categories"].get("self-harm/intent", False),
            self_harm_instructions=result["categories"].get("self-harm/instructions", False),
            harassment_threatening=result["categories"].get("harassment/threatening", False),
            violence=result["categories"].get("violence", False)
        )
        
        category_scores = CategoryScores(
            sexual=result["category_scores"].get("sexual", 0.0),
            hate=result["category_scores"].get("hate", 0.0),
            harassment=result["category_scores"].get("harassment", 0.0),
            self_harm=result["category_scores"].get("self-harm", 0.0),
            sexual_minors=result["category_scores"].get("sexual/minors", 0.0),
            hate_threatening=result["category_scores"].get("hate/threatening", 0.0),
            violence_graphic=result["category_scores"].get("violence/graphic", 0.0),
            self_harm_intent=result["category_scores"].get("self-harm/intent", 0.0),
            self_harm_instructions=result["category_scores"].get("self-harm/instructions", 0.0),
            harassment_threatening=result["category_scores"].get("harassment/threatening", 0.0),
            violence=result["category_scores"].get("violence", 0.0)
        )
        
        moderation_result = ModerationResult(
            flagged=result.get("flagged", False),
            categories=categories,
            category_scores=category_scores
        )
        results.append(moderation_result)

    return ModerationResponse(
        id=json_response.get("id", ""),
        model=json_response.get("model", ""),
        results=results
    )
async def moderate(text: str) -> Union[dict, None]:
    return moderation_json_to_class(await moderate_raw(text)).get_true_categories()

#! END MODERATION

#! CHAT
class ChatRole(Enum):
    User = "user"
    Assistant = "assistant"
    System = "system"
class ChatMessage:
    def __init__(self, role: ChatRole, content: str):
        self.role = role
        self.content = content
    def to_json(self) -> dict:
        return {
            "role": self.role.value,
            "content": self.content
        }

class ChatHistory:
    def __init__(self, messages: list[ChatMessage]):
        self.messages = messages

    def __add__(self, other):
        return ChatHistory(self.messages + other.messages)
    def cut(self, count_excluding_system: int, dont_change_self: bool = False):
        # leave in self.messages only first if role is System and last count_excluding_system

        if dont_change_self:
            msgs = self.messages.copy()
            iter = 0
            for msg in reversed(msgs):
                if msg.role == ChatRole.System:
                    iter += 1
                if iter > count_excluding_system:
                    msgs.remove(msg)
            return ChatHistory(msgs)
        else:
            iter = 0
            for msg in reversed(self.messages):
                if msg.role == ChatRole.System:
                    iter += 1
                if iter > count_excluding_system:
                    self.messages.remove(msg)
    def to_json(self) -> dict:
        return [message.to_json() for message in self.messages]
    def add_message(self, message: ChatMessage):
        self.messages.append(message)
    def get_last_message(self) -> ChatMessage:
        return self.messages[-1]
    def get_last_user_message(self) -> ChatMessage:
        return next((message for message in reversed(self.messages) if message.role == ChatRole.User), None)
    def get_last_assistant_message(self) -> ChatMessage:
        return next((message for message in reversed(self.messages) if message.role == ChatRole.Assistant), None)
    def update_system_message(self, message: ChatMessage):
        for message in self.messages:
            if message.role == ChatRole.System:
                message.content = message.content
                return
        if not any(message.role == ChatRole.System for message in self.messages):
            self.messages.insert(0, ChatMessage(ChatRole.System, message.content))

def chat_json_to_class(json_response: dict) -> ChatHistory:
    return ChatHistory(
        messages=[ChatMessage(ChatRole(message["role"]), message["content"]) for message in json_response]
    )
class ChatCompletion:
    def __init__(self, id: str, object: str, created: int, model: str, choices: list, usage: dict):
        self.id = id
        self.object = object
        self.created = created
        self.model = model
        self.choices = [ChatChoice(**choice) for choice in choices]
        self.usage = Usage(**usage)  # Добавлено поле usage
    def to_json(self) -> dict:
        return {
            "id": self.id,
            "object": self.object,
            "created": self.created,
            "model": self.model,
            "choices": [choice.to_json() for choice in self.choices],
            "usage": self.usage.to_json()
        }
    
class Usage:
    def __init__(self, prompt_tokens: int, completion_tokens: int, total_tokens: int):
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = total_tokens
    def to_json(self) -> dict:
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens
        }
class ChatChoice:
    def __init__(self, index: int, message: dict, finish_reason: str):
        self.index = index
        self.message = ChatMessage(ChatRole(message["role"]), message["content"])
        self.finish_reason = finish_reason
    def to_json(self) -> dict:
        return {
            "index": self.index,
            "message": self.message.to_json(),
            "finish_reason": self.finish_reason
        }


def json_to_chat_completion(json_response: dict) -> ChatCompletion:
    # print(json_response)
    return ChatCompletion(
        id=json_response.get("id","null"),
        object=json_response.get("object"),
        created=json_response["created"],
        model=json_response["model"],
        choices=json_response["choices"],
        usage=json_response.get("usage", {})  # Добавлено получение usage
    )
async def post_chat_completion_raw(messages: ChatHistory, model: ChatModels = ChatModels.GPT4o) -> dict:
    url = 'https://cablyai.com/v1/chat/completions'
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {
        'model': model.value,
        'messages': messages.to_json(),
        'stream': False
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            json_response = await response.json()
            return json_response
async def chat_completion(messages: ChatHistory, model: ChatModels = ChatModels.GPT4o) -> ChatCompletion:
    return json_to_chat_completion(await post_chat_completion_raw(messages, model))

#! END CHAT



#! IMAGE
class ImageResponse:
    def __init__(self, created: int, data: list):
        self.created = created
        self.data = [ImageData(item["url"]) for item in data]

    async def download_images(self, path: str = "images", filename: str = "image"):
        for index, image in enumerate(self.data):
            await image.download(path, filename, index)

class ImageData:
    def __init__(self, url: str):
        self.url = url

    async def download(self, path: str = "images", filename: str = "image", index: int = 0):
        os.makedirs(path, exist_ok=True)
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                if response.status == 200:
                    image_data = await response.read()
                    filename = f"{path}/{filename}_{index}.png"
                    with open(filename, 'wb') as f:
                        f.write(image_data)
                else:
                    print(f"Ошибка при загрузке изображения: {response.status}")



def json_to_image_response(json_response: dict) -> ImageResponse:
    return ImageResponse(created=json_response["created"], data=json_response["data"])

async def post_image_generation(prompt: str, n: int = 1, size: str = "1024x1024", response_format: str = "url", model: Text2ImgModels = Text2ImgModels.FLUX1Dev):
    url = 'https://cablyai.com/v1/images/generations'
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {
        'prompt': prompt,
        'n': n,
        'size': size,
        'response_format': response_format,
        'model': model.value
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            json_response = await response.json()
            return json_to_image_response(json_response)


#! END IMAGE
# event_loop = asyncio.new_event_loop()
# asyncio.set_event_loop(event_loop)
# output = event_loop.run_until_complete(post_image_generation("a villa in space orbiting Mars, in the style of futurism", n=1, size="1024x1024", response_format="url", model=Text2ImgModels.FLUX1Dev))
# print(output.data[0].url)
# event_loop.run_until_complete(output.download_images(path="images", filename="mars_villa"))
