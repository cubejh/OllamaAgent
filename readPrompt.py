import re
import json
import requests
from readAPI import load_api_key
from Otools.tools_init import tool_map, TOOL_PROMPTS

BASE_URL = "https://api-gateway.netdb.csie.ncku.edu.tw/api/generate"


# -------------------------
# Tool selector system prompt
# -------------------------
PROMPT_TOOL_SELECTOR = """
你主要是一個工具調度器，不須工具時也可以回答問題。
根據用戶問題，決定是否需要工具，以及用什麼工具。

可用工具：
{tool_prompts}

只輸出純 JSON，不要加其他文字。
JSON 輸出格式：
{{
  "tool": "<tool_name>",
  "args": {{ ... }}
}}

若不需要工具即可回答：
{{
  "tool": null,
  "reply": "..."
}}

使用者問題：
"{user_input}"
"""

# -------------------------
# After tool execution – reply prompt
# -------------------------
PROMPT_REPLY = """
使用者原本的問題：
{user_input}

以下是工具產生的資料：
{tool_result}

請用使用者原本的問題中的語言，搭配自然語氣與表情符號回覆使用者。
"""


def call_llm(prompt, api_key):
    payload = {
        "model": "gemma3:4b",
        "prompt": prompt,
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


def read_Prompt(user_input, api_key):
    """This is the main tool agent"""
    # -------------------------
    # choose tools or not
    # -------------------------
    decision_prompt = PROMPT_TOOL_SELECTOR.format(
        user_input=user_input,
        tool_prompts=TOOL_PROMPTS
    )

    decision_raw = call_llm(decision_prompt, api_key)
    print(decision_raw)
    cleaned = re.sub(r"```(?:json)?\n(.*?)```", r"\1", decision_raw, flags=re.S).strip()

    try:
        decision = json.loads(cleaned)
    except json.JSONDecodeError:
        return "tool select jason fail：\n" + decision_raw

    # -------------------------
    # no need any tool, reply
    # -------------------------
    if decision["tool"] is None:
        return decision["reply"]

    # -------------------------
    # need tool → tools/
    # -------------------------
    tool_name = decision["tool"]
    args = decision["args"]

    if tool_name not in tool_map:
        return f"unknown tool：{tool_name}"

    tool_func = tool_map[tool_name]

    tool_result = tool_func(**args)

    # -------------------------
    # llm reply
    # -------------------------
    reply_prompt = PROMPT_REPLY.format(
        user_input=user_input,
        tool_result=tool_result
    )
    final_answer = call_llm(reply_prompt, api_key)
    return final_answer
