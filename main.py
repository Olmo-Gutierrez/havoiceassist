from fastapi import FastAPI, Request
import openai
import requests
import os

app = FastAPI()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HA_TOKEN = os.getenv("HA_TOKEN")
HA_URL = os.getenv("HA_URL")

openai.api_key = OPENAI_API_KEY

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    messages = data.get("messages", [])

    functions = [
        {
            "name": "turn_on_light",
            "description": "Turn on a light in Home Assistant",
            "parameters": {
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Entity ID of the light to turn on"
                    }
                },
                "required": ["entity_id"]
            }
        }
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4-0613",
        messages=messages,
        functions=functions,
        function_call="auto"
    )

    choice = response.choices[0]
    if choice.finish_reason == "function_call":
        func_name = choice.message.function_call.name
        arguments = eval(choice.message.function_call.arguments)
        if func_name == "turn_on_light":
            result = call_ha_service("light", "turn_on", arguments)
            return {"result": result}
    else:
        return {"response": choice.message.content}

def call_ha_service(domain, service, data):
    url = f"{HA_URL}/api/services/{domain}/{service}"
    headers = {
        "Authorization": f"Bearer {HA_TOKEN}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()