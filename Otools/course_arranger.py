import requests
from Otools.get_data_path import get_data_path

TOOL_PROMPT = '4. course_arranger：寫入預排。格式 {{ "ID": "課程代碼" }}\n'

def CSVReader(fileName):
    file_path = get_data_path(fileName)
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()
    return 

def CourseSearcher(id,fileName):
    return False

def CourseReacordSearch(id,fileName="CourseInfo.csv"):
    courseInfo = CSVReader(fileName)
    #get id search
    #
    return ""#True->exsist

def CourseArrangeSearch(id,fileName="CourseArrange.csv"):
    courseInfo = CSVReader(fileName)
    #get id search
    #
    return ""#True->exsist

def CourseArrangeWrite(id,fileName="CourseArrange.csv"): #True for conflict
    #write and check conflict
    return ""

def CourseArranger(id):
    if not CourseReacordSearch(id):
        return "尚未查詢到此課程"
    if CourseArrangeSearch(id):
        return "已經存在預排中了"
    Conflict = CourseArrangeWrite(id)
    if Conflict:
        return "預排成功，但與現有課程衝突"
    return "預排成功"

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
