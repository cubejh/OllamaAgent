from Otools.weather import weather_tool, TOOL_PROMPT as WEATHER_PROMPT

tool_map = {
    "weather": weather_tool
}

TOOL_PROMPTS = "\n".join([WEATHER_PROMPT,""])

# join your prompt if adding tools