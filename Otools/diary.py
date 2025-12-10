import os
import requests
from Otools.shortAsk import short_ask

TOOL_PROMPT = '1.diary：這是日記工具，寫入、查詢與刪除(刪除不須再次確認)。格式 {{ "mode": "write"(寫入)或"search"(查詢)或"delete"(刪除), "content": "使用者內容(刪除時給"刪除")" }}\n'
APPEND_PROMPT = "你是日記整理器，這是日記內容，請幫我依照日期或資訊整理，並直接給我整理後的結果"

def diary_tool(mode, content):
    if(mode=="write"):
        return write_diary(content)
    if(mode=="search"):
        return read_diary()
    if(mode=="delete"):
        return delete_diary()
    return "Something Wrong..."
def get_diary_path(filename="diary_data.txt"):
    """get diary_data.txt path"""
    this_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(this_dir)
    target_dir = os.path.join(project_root, "diary_data")
    os.makedirs(target_dir, exist_ok=True)

    file_path = os.path.join(target_dir, filename)

    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            pass
    return file_path


def write_diary(content, filename="diary_data.txt"):
    """Auto sort by date by Ollama"""
    write_content = short_ask(APPEND_PROMPT+read_diary()+"\n"+content)
    file_path = get_diary_path(filename)
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(write_content + "\n")
    return "日記寫入成功"


def read_diary(filename="diary_data.txt"):
    file_path = get_diary_path(filename)
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def delete_diary(filename="diary_data.txt"):
    """delete diary_data.txt"""
    file_path = get_diary_path(filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return "日記檔案已刪除"