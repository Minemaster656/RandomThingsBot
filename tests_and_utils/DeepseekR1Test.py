from openai import OpenAI

import private.coreData

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=private.coreData.API_KEYS["openrouter"],
)

completion = client.chat.completions.create(
  # extra_headers={
  #   "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
  #   "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
  # },
  extra_body={},
  model="deepseek/deepseek-r1:free",
  messages=[
    {
      "role": "user",
      "content": "Сколько букв r в слове strawberry?"
    }
  ]
)
print(completion.choices[0].message.content)
print(completion)
print(completion.choices[0].message)