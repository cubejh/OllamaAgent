# gen by AI directly, only for test, please fill in API key

import requests
import json
import re


API_KEY = ""#fill in your api key
BASE_URL = "https://api-gateway.netdb.csie.ncku.edu.tw/api/generate"

# Prompt 
PROMPT_EXTRACT_CITY = """
Extract the city name from the following question. 
Only output the city name, nothing else.

Question:
{query}
"""

PROMPT_WEATHER_ANSWER = """
You are a smart weather assistant. Answer in the same language as the user's question.
Please answer the user's question based on the following data.

User question:
{query}

Fetched weather data:
{weather_info}

Answer in clear natural language.
"""

# input
query = input("User question: ").strip()
print(f"\nUser question: {query}\n")


# city name

payload_city = {
    "model": "gemma3:4b",
    "prompt": PROMPT_EXTRACT_CITY.format(query=query),
    "stream": False
}

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

try:
    response_city = requests.post(BASE_URL, json=payload_city, headers=headers)
    response_city.raise_for_status()

    city_name = ""
    for line in response_city.content.splitlines():  # use bytes
        if not line.strip():
            continue
        obj = json.loads(line.decode("utf-8"))
        if "response" in obj:
            city_name += obj["response"]

    city_name = city_name.strip()
    if not city_name:
        city_name = "New York"  # fallback
    print(f"Extracted city: {city_name}")

except Exception as e:
    print("City extraction failed:", e)
    city_name = "New York"

# -------------------------
# 5️⃣ Fetch weather data
# -------------------------
try:
    weather_res = requests.get(f"https://wttr.in/{city_name}?format=j1")
    weather_res.raise_for_status()
    data = weather_res.json()
    current = data["current_condition"][0]

    temp_c = current["temp_C"]
    weather_desc = current["weatherDesc"][0]["value"]
    humidity = current["humidity"]

    weather_info = f"City: {city_name}\nTemperature: {temp_c}°C\nWeather: {weather_desc}\nHumidity: {humidity}%"

except Exception as e:
    weather_info = f"Failed to fetch weather data: {e}"

print("Fetched weather data:\n", weather_info, "\n")

# -------------------------
# 6️⃣ Send data to model for natural language answer
# -------------------------
prompt_answer = PROMPT_WEATHER_ANSWER.format(query=query, weather_info=weather_info)

payload_answer = {
    "model": "gemma3:4b",
    "prompt": prompt_answer,
    "stream": False
}

try:
    response_answer = requests.post(BASE_URL, json=payload_answer, headers=headers)
    response_answer.raise_for_status()

    full_text = ""
    for line in response_answer.content.splitlines():  # use bytes
        if not line.strip():
            continue
        obj = json.loads(line.decode("utf-8"))
        if "response" in obj:
            full_text += obj["response"]

    print("=== Model answer ===")
    print(full_text)

except Exception as e:
    print("Answer generation failed:", e)
