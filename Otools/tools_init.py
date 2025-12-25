from Otools.weather import weather_tool, TOOL_PROMPT as WEATHER_PROMPT
from Otools.diary import diary_tool, TOOL_PROMPT as DIARY_PROMPT
from Otools.course_info_tool import course_info_tool, TOOL_PROMPT as COURSE_INFO_PROMPT
from Otools.course_arranger import course_arranger, TOOL_PROMPT as COURSEARRANGER_PROMPT

tool_map = {
    "weather": weather_tool,
    "diary": diary_tool,
    "course_info": course_info_tool,
    "course_arranger": course_arranger
}

TOOL_PROMPTS = "\n".join([DIARY_PROMPT, WEATHER_PROMPT, COURSE_INFO_PROMPT, COURSEARRANGER_PROMPT,""])

# join your prompt if adding tools