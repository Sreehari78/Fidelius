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
import pydantic
from pydantic import BaseModel

class ResponseFormat(BaseModel):
    changed_names: list[str]
def chatlocal(system,content):
    system="You are a bot that ofuscates by changing the values by: "+system +"Return only changed values in the original fomrat and nothing else as a comma seperated list"
    # url = "http://127.0.0.1:1234/v1/chat/completions"
    # headers = {
    #     "Content-Type": "application/json"
    # }
    # data = {
    #     "model": "dolphin-2.8-mistral-7b-v02",
    #     "messages": [
    #         {"role": "system", "content": system},
    #         {"role": "user", "content": content}
    #     ],
    #     # "response_format": ResponseFormat,
    #     "temperature": 0.7,
    #     "max_tokens": -1,
    #     "stream": False
    # }
    # # Sending the POST request to the API
    # response = requests.post(url, headers=headers, data=json.dumps(data), stream=True)
    # print("Response from the API:")
    # print(response.json())
    # return response.json()["choices"][0]["message"]["content"]
    from openai import OpenAI
    import json
    client = OpenAI(api_key="")

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": system
            },
            {
                "role": "user",
                "content": content
            }
            
        ],
        response_format=ResponseFormat,
    )
    print(json.loads(completion.choices[0].message.content)["changed_names"])
    response = json.loads(completion.choices[0].message.content)["changed_names"]
    comma_separated_string = ",".join(response)
    return comma_separated_string
