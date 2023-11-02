import g4f

import utils

g4f.logging = True # enable logging
g4f.check_version = False # Disable automatic version checking
print(g4f.version) # check version
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
async def askGPT(system_prompt : str, user_prompt : str, useGPT4 : bool):
    messages = []
    if not utils.checkStringForNoContent(system_prompt):
        messages.append({{"role": "system", "content": f"{system_prompt}"}})
    messages.append({"role": "user", "content": f"{user_prompt}"})
    # normal response
    response = g4f.ChatCompletion.create(
        model= g4f.models.gpt_4 if useGPT4 else "gpt-3.5-turbo",
        messages=messages,
    )  # alternative model setting

    return response