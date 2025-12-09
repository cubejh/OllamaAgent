from Otools.weather import weather_tool, TOOL_PROMPT as WEATHER_PROMPT
from Otools.diary import diary_tool, TOOL_PROMPT as DIARY_PROMPT

tool_map = {
    "weather": weather_tool,
    "diary": diary_tool
}

TOOL_PROMPTS = "\n".join([DIARY_PROMPT,WEATHER_PROMPT,""])

# join your prompt if adding tools