# gen by AI directly, only for test, please fill in API key

import requests
import json

API_KEY = ""#fill in your api key
BASE_URL = "https://api-gateway.netdb.csie.ncku.edu.tw/api/generate"
prompt = "你是什麼模型？"



payload = {
    "model": "gemma3:4b",
    "prompt": prompt,
    "stream": True  
}

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

try:
    response = requests.post(BASE_URL, json=payload, headers=headers)
    response.raise_for_status()

    print("=== 原始回傳每行解析 ===")
    full_text = ""
    for line in response.text.splitlines():
        if line.strip() == "":
            continue
        obj = json.loads(line)
        if "response" in obj:
            full_text += obj["response"]

    print("\n=== 模型回答 ===")
    print(full_text)

except requests.exceptions.HTTPError as e:
    print("HTTP 錯誤：", e)
except requests.exceptions.RequestException as e:
    print("連線錯誤：", e)