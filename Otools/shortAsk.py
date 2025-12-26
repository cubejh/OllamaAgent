import json
import requests
from readConfig import load_config

BASE_URL = "https://api-gateway.netdb.csie.ncku.edu.tw/api/generate"

def short_ask(user_input):
    """short asking question example"""
    api_key = load_config(".env")["API_key"]
    model = load_config(".env")["Model"]
    payload = {
        "model": model,
        "prompt": user_input,
        "stream": False
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    response = requests.post(BASE_URL, json=payload, headers=headers)
    response.raise_for_status()


    text = ""
    for line in response.content.splitlines():
        if not line.strip():
            continue
        obj = json.loads(line.decode("utf-8"))
        if "response" in obj:
            text += obj["response"]

    return text.strip()

"""
if __name__ == "__main__":
    api_key = load_api_key()
    question = input("question：")
    answer = short_ask(question, api_key)
    print("Ollama output:", answer)
"""