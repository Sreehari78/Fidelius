# from openai import OpenAI
# from dotenv import load_dotenv
# load_dotenv(".env")
# def chatopenai(system,content):
#     client = OpenAI(api_key=os.getenv('OPENAI_API'))
#     completion = client.chat.completions.create(
#     model="gpt-4o-mini",
#     messages=[
#         {"role": "system", "content": system},
#         {
#             "role": "user",
#             "content": content
#         }
#     ]
#     )
#     print(completion.choices[0].message)
#     return completion.choices[0].message


import requests
import json
def chatlocal(system,content):
    url = "http://127.0.0.1:1234/v1/chat/completions"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama-3.2-1b-instruct",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": content}
        ],
        "temperature": 0.7,
        "max_tokens": -1,
        "stream": False
    }
    # Sending the POST request to the API
    response = requests.post(url, headers=headers, data=json.dumps(data), stream=True)
    return response.json()["choices"][0]["message"]["content"]
