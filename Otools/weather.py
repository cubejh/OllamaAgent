import requests

TOOL_PROMPT = '1. weather：查詢天氣。格式 {{ "city": "城市", "day": "today" }}\n'

def weather_tool(city, day="today"):
    try:
        res = requests.get(f"https://wttr.in/{city}?format=j1")
        data = res.json()

        current = data["current_condition"][0]
        temp = current["temp_C"]
        desc = current["weatherDesc"][0]["value"]
        hum  = current["humidity"]

        return f"{city} | Temp: {temp}°C | {desc} | Humidity: {hum}%"

    except Exception as e:
        return f"Weather tool error: {str(e)}"
