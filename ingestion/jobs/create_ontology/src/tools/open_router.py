import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()  # Load variables from .env

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def post_to_llm(message):
    return requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        data=json.dumps({
                "model": "mistral/ministral-8b",
                "messages": [
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                "temperature": 0.1,
                "top_k": 1
            })
        )