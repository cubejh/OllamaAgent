# Otools/course_info_tool.py
# pip install selenium webdriver-manager beautifulsoup4

import re
from typing import List, Dict, Any, Optional, Tuple

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import os
import csv
from Otools.get_data_path import get_data_path

ENTRY_URL = "https://course.ncku.edu.tw/index.php?c=qry11215&m=en_query"
TYPE_ZH = {"Required": "必修", "Elective": "選修"}

# ✅ 給 tool selector 的 prompt（tools_init.py 會用到）
TOOL_PROMPT = (
    "3.course_info：查詢成大選課系統（低頻、單次查詢），輸入「學院、系所、年級」，回傳課程清單（課程代碼/課名/學分/必選修/老師/上課時間/教室）。\n"
    '格式 { "college": "電機資訊學院", "dept": "資訊系", "degree": "大二", "headless": true }\n'
)
# -----------------------------
# 1) College + Dept Mapping
# -----------------------------
COLLEGE_CODE = {
    "文學院": "N",
    "理學院": "P",
    "工學院": "Q",
    "管理學院": "R",
    "醫學院": "S",
    "社會科學院": "U",
    "電機資訊學院": "V",
    "規劃與設計學院": "W",
    "生物科學與科技學院": "Z",
}

# 每個學院底下：系所名稱 -> dept_no
DEPT_CODE = {
    "文學院": {
        "文學院學士班": "B0", "中文系": "B1", "外文系": "B2", "歷史系": "B3", "台文系": "B5",
        "中文所": "K1", "外文所": "K2", "歷史所": "K3", "藝術所": "K4", "台文所": "K5",
        "考古所": "K7", "戲劇碩士學程": "K8", "文學院研究所": "KZ",
    },
    "理學院": {
        "數學系": "C1", "物理系": "C2", "化學系": "C3", "地科系": "C4", "光電系": "F8",
        "應數所": "L1", "物理所": "L2", "化學所": "L3", "地科所": "L4", "光電所": "L7", "電漿所": "LA",
        "發光二極體碩士": "VF", "光電科技產碩": "VP",
    },
    "工學院": {
        "工學院": "E0", "機械系": "E1", "化工系": "E3", "資源系": "E4", "材料系": "E5",
        "土木系": "E6", "水利系": "E8", "工科系": "E9", "能源學程": "F0", "系統系": "F1",
        "航太系": "F4", "環工系": "F5", "測量系": "F6", "醫工系": "F9", "機械產碩": "VQ",
        "工程管理碩專": "N0", "機械所": "N1", "化工所": "N3", "資源所": "N4", "材料所": "N5",
        "土木所": "N6", "水利所": "N8", "工科所": "N9", "海事所": "NA",
        "尖端碩士學程": "NB", "自災碩士學程": "NC", "智慧製造碩士學程": "NF",
        "能源碩士學程": "P0", "系統所": "P1", "航太所": "P4", "環工所": "P5", "測量所": "P6",
        "醫工所": "P8", "民航所": "Q4", "太空所": "Q8",
    },
    "管理學院": {
        "會計系": "H1", "統計系": "H2", "工資系": "H3", "企管系": "H4", "交管系": "H5", "管理學院": "HZ",
        "EMBA碩專": "R0", "會計所": "R1", "統計所": "R2", "工資所": "R3", "企管所": "R4", "交管所": "R5",
        "國企所": "R6", "資管所": "R7", "財金所": "R8", "電管所": "R9", "國經所": "RA", "體健所": "RB",
        "AMBA碩士學程": "RD", "數據所": "RE", "經營博士學程": "RF", "管理學院研究所": "RZ",
        "財金產碩": "VR", "東南亞金融產碩": "VT", "經營管理產碩": "VY",
    },
    "醫學院": {
        "醫學院學士班": "I0", "護理系": "I2", "醫技系": "I3", "醫學系": "I5", "物治系": "I6",
        "職治系": "I7", "藥學系": "I8", "牙醫系": "I9", "公衛系": "IA",
        "醫學院研究所": "S0", "生化所": "S1", "藥理所": "S2", "生理所": "S3", "微免所": "S4", "基醫所": "S5",
        "臨藥科技所": "S6", "環醫所": "S7", "行醫所": "S8", "臨醫所": "S9", "神經博士學程": "SA",
        "公衛碩專": "SB", "食安所": "SC",
        "分醫所": "T1", "護理所": "T2", "醫技所": "T3", "口醫所": "T4",
        "物治所": "T6", "職治所": "T7", "公衛所": "T8", "細胞所": "T9", "健照所": "TA", "老年所": "TC",
    },
    "社會科學院": {
        "社會科學院": "D0", "法律系": "D2", "政治系": "D4", "經濟系": "D5", "心理系": "D8",
        "政經所": "U1", "法律所": "U2", "教育所": "U3", "經濟所": "U5", "心理所": "U7", "心智應用博士學程": "U8",
    },
    "電機資訊學院": {
        "電機系": "E2", "電資學院學士班": "EZ", "資訊系": "F7",
        "電機所": "N2", "多媒博士學程": "ND", "人工智慧博士學程": "NE", "資安碩士學程": "NQ",
        "資訊所": "P7", "製造所": "P9", "微電所": "Q1", "電通所": "Q3",
        "醫資所": "Q5", "南科碩專": "Q6", "奈積碩專": "Q7", "電資學院研究所": "QZ",
        "電力產碩": "V6", "微波材料產碩": "V8", "電子材料產碩": "V9",
        "電機產碩": "VA", "光材產碩": "VB", "光產產碩": "VC", "微波材料光升產碩": "VD", "電子產碩": "VE",
        "靜電保護產碩": "VG", "磁性材料產碩": "VH", "電機驅動產碩": "VK", "積體製程產碩": "VM",
        "微波元件產碩": "VN", "光進程產碩": "VO", "金融資訊產碩": "VS", "智慧製造產碩": "VU",
        "光電半導體產碩": "VV", "光電材料產碩": "VW", "資訊產碩": "VX",
    },
    "規劃與設計學院": {
        "建築系": "E7", "都計系": "F2", "工設系": "F3", "規劃設計學院學士班": "FZ",
        "建築所": "N7", "都計所": "P2", "工設所": "P3", "創意所": "PA", "科藝碩士學程": "PB", "規劃設計學院研究所": "PZ",
    },
    "生物科學與科技學院": {
        "生科系": "C5", "生技系": "C6", "生科學院": "Z0",
        "生科所": "L5", "生技所": "L6", "生訊所": "Z2", "熱植所": "Z3", "譯農博士學程": "Z5",
    },
}

def normalize_degree(degree: str) -> str:
    """
        raw degree str to degree str
    """
    d = (degree or "").strip()
    
    mapping = {
        "大一": "1", "大二": "2", "大三": "3", "大四": "4",
        "大1": "1", "大2": "2", "大3": "3", "大4": "4",
        "1": "1", "2": "2", "3": "3", "4": "4",
    }
    return mapping.get(d, d)

def map_to_codes(college: str, dept: str) -> Tuple[str, str]:
    """
    Docstring for map_to_codes
    :param college: Description
    :type college: str
    :param dept: Description
    :type dept: str
    :return: Description
    :rtype: Tuple[str, str]
    """
    college = (college or "").strip()
    dept = (dept or "").strip()

    if college not in COLLEGE_CODE:
        raise KeyError(f"找不到學院：{college}（可用：{', '.join(COLLEGE_CODE.keys())}）")

    dept_map = DEPT_CODE.get(college, {})
    if dept not in dept_map:
        raise KeyError(f"找不到系所：{dept}（{college} 可用：{', '.join(dept_map.keys())}）")

    return COLLEGE_CODE[college], dept_map[dept]

# -----------------------------
# Parser
# -----------------------------
def _uniq_keep(seq: List[str]) -> List[str]:
    seen = set()
    out = []
    for x in seq:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out

def _pick_course_table(soup: BeautifulSoup):
    for t in soup.find_all("table"):
        txt = t.get_text(" ", strip=True)
        # eng ver.
        if ("Credits" in txt and ("Elective" in txt or "Required" in txt)):
            return t
        # chinese ver.
        if ("學分" in txt and ("必修" in txt or "選修" in txt)):
            return t
    return None

def _find_header_row(table) -> Optional[Any]:
    for tr in table.find_all("tr"):
        if tr.find("th"):
            return tr
    return None

def _find_idx(headers: List[str], keywords: List[str]) -> Optional[int]:
    for i, h in enumerate(headers):
        hl = h.lower()
        if any(k.lower() in hl for k in keywords):
            return i
    return None

def _split_credits_and_type(raw: str) -> Tuple[str, str]:
    raw = (raw or "").strip()
    if not raw:
        return "", ""
    m_credit = re.search(r"(\d+)", raw)
    credits = m_credit.group(1) if m_credit else ""
    m_type = re.search(r"\b(Required|Elective)\b", raw)
    typ = m_type.group(1) if m_type else ""
    return credits, typ

def _extract_time_and_rooms_from_cell(td) -> Tuple[List[str], List[str]]:
    cell_text = td.get_text(" ", strip=True)
    pattern = r"\[\d+\]\s*[A-Za-z0-9]+(?:\s*~\s*[A-Za-z0-9]+)?"
    time_slots = [re.sub(r"\s+", "", s) for s in re.findall(pattern, cell_text)]

    rooms = []
    for a in td.find_all("a"):
        href = (a.get("href") or "")
        if href.startswith("javascript:maps"):
            room = a.get_text(" ", strip=True)
            if room:
                rooms.append(room)

    return _uniq_keep(time_slots), _uniq_keep(rooms)

def _find_time_room_td_fallback(tr) -> Optional[Any]:
    for td in tr.find_all("td"):
        td_html = str(td)
        if "javascript:maps" in td_html:
            return td
        if td.select_one("div.flex_time"):
            return td
    return None

def parse_courses(html: str) -> List[Dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    table = _pick_course_table(soup)
    if table is None:
        return []

    header_row = _find_header_row(table)
    headers = []
    if header_row is not None:
        headers = [c.get_text(" ", strip=True) for c in header_row.find_all(["th", "td"])]

    i_dept = _find_idx(headers, ["Dept", "Inst"]) if headers else None
    i_credits = _find_idx(headers, ["Credits"]) if headers else None
    i_er = _find_idx(headers, ["Elective", "Required"]) if headers else None
    i_teacher = _find_idx(headers, ["Instructor"]) if headers else None

    courses: List[Dict[str, Any]] = []
    seen = set()

    for tr in table.find_all("tr"):
        if header_row is not None and tr is header_row:
            continue

        tds = tr.find_all("td")
        if not tds:
            continue

        name_a = tr.select_one("span.course_name a")
        course_name = name_a.get_text(strip=True) if name_a else ""
        if not course_name:
            continue

        seq_div = tr.select_one("div.dept_seq")
        course_code = seq_div.get_text(strip=True) if seq_div else ""

        col_texts = [td.get_text(" ", strip=True) for td in tds]

        def get(i: Optional[int]) -> str:
            return col_texts[i] if i is not None and i < len(col_texts) else ""

        dept = get(i_dept) if i_dept is not None else (tds[0].get_text(" ", strip=True) if tds else "")
        credits_raw = get(i_credits)
        er_raw = get(i_er)
        teacher = get(i_teacher)

        c1, t1 = _split_credits_and_type(credits_raw)
        c2, t2 = _split_credits_and_type(er_raw)
        credits = c1 or c2
        typ = t2 or t1
        typ_zh = TYPE_ZH.get(typ, typ)

        time_slots, rooms = [], []
        td_time = _find_time_room_td_fallback(tr)
        if td_time is not None:
            time_slots, rooms = _extract_time_and_rooms_from_cell(td_time)

        item = {
            "系所": dept,
            "課程代碼": course_code,
            "課名": course_name,
            "學分": credits,
            "必選修": typ_zh,
            "老師": teacher,
            "上課時間": time_slots,
            "教室": rooms,
        }

        key = (item["課程代碼"], item["課名"], item["老師"], tuple(item["上課時間"]), tuple(item["教室"]))
        if key in seen:
            continue
        seen.add(key)

        courses.append(item)

    return courses

# -----------------------------
# Selenium Query
# -----------------------------
def select_degree(wait: WebDriverWait, degree_label: str) -> Tuple[bool, str]:
    degree_el = wait.until(EC.presence_of_element_located((By.ID, "sel_degree")))
    sel = Select(degree_el)

    try:
        sel.select_by_value(degree_label)
        return True, f"value={degree_label}"
    except Exception:
        pass

    try:
        sel.select_by_visible_text(degree_label)
        return True, f"text={degree_label}"
    except Exception:
        return False, f"not found: {degree_label}"

def _query_once(col: str, dept_no: str, degree_label: str, headless: bool) -> Dict[str, Any]:
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 30)

    try:
        driver.get(ENTRY_URL)

        Select(wait.until(EC.presence_of_element_located((By.ID, "sel_col")))).select_by_value(col)
        Select(wait.until(EC.presence_of_element_located((By.ID, "sel_dept")))).select_by_value(dept_no)

        ok_degree, how = select_degree(wait, degree_label)
        if not ok_degree:
            degree_el = wait.until(EC.presence_of_element_located((By.ID, "sel_degree")))
            sel = Select(degree_el)
            opts = [(o.text, o.get_attribute("value")) for o in sel.options]
            return {"ok": False, "error": f"選不到年級：{how}", "degree_options": opts}

        btn = wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//button[contains(.,'Search') or contains(.,'查詢') or contains(.,'搜尋')]"
            " | //input[contains(@value,'Search') or contains(@value,'查詢') or contains(@value,'搜尋')]"
        )))
        
        btn.click()

        wait.until(lambda d: "&i=" in d.current_url)           # URL -> &i= result page
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))  # table...

        # force to english ver.
        ok = force_switch_to_english(driver, wait)
        if not ok:
            return {"ok": False, "error": "切換英文失敗（找不到 setLang 或 ENGLISH 按鈕）", "current_url": driver.current_url}
        
        html = driver.page_source
        courses = parse_courses(html)

        return {
            "ok": True,
            "fixed": {"col": col, "dept_no": dept_no},
            "degree": {"input": degree_label, "selected_by": how},
            "count": len(courses),
            "courses": courses,
        }

    except TimeoutException as e:
        return {"ok": False, "error": f"等待逾時：{e}", "current_url": driver.current_url}
    finally:
        driver.quit()

# -----------------------------
# Clean string output
# -----------------------------
def _format_clean(result: Dict[str, Any]) -> str:
    if not result.get("ok"):
        lines = ["Course tool error: " + result.get("error", "unknown")]
        if "degree_options" in result:
            lines.append("degree_options:")
            for t, v in result["degree_options"]:
                lines.append(f"- {t} ({v})")
        return "\n".join(lines)

    lines = []
    lines.append(f"col: {result['fixed']['col']} | dept_no: {result['fixed']['dept_no']} | degree: {result['degree']['input']}")
    lines.append(f"count: {result.get('count', 0)}")
    lines.append("=" * 50)

    for c in result.get("courses", []):
        ts = ", ".join(c.get("上課時間", []) or [])
        rooms = ", ".join(c.get("教室", []) or [])
        lines.append(f"系所：{c.get('系所', '')}")
        lines.append(f"課程代碼：{c.get('課程代碼', '')}")
        lines.append(f"課名：{c.get('課名', '')}")
        lines.append(f"學分：{c.get('學分', '')}")
        lines.append(f"必選修：{c.get('必選修', '')}")
        lines.append(f"老師：{c.get('老師', '')}")
        lines.append(f"上課時間：{ts}")
        lines.append(f"教室：{rooms}")
        lines.append("-" * 50)

    return "\n".join(lines)

# -----------------------------
# Tool entry
# -----------------------------

def write_courses_to_csv(
    result: Dict[str, Any],
    csv_path: str,
    college_code: str,
    dept_code: str,
    degree_label: str,
):
    # CSV header (all English)
    fieldnames = [
        "course_code",   # 課程代碼
        "time",          # 上課時間 (joined)
        "course_name",   # 課名
        "credits",       # 學分
        "college_code",  # 學院代碼
        "dept_code",     # 科系代碼
        "grade",         # 年級
        "required",      # Required/Elective
    ]

    file_exists = os.path.exists(csv_path)

    # Convert Chinese type -> English
    type_map = {
        "必修": "Required",
        "選修": "Elective",
        "": "",
        None: "",
    }

    with open(csv_path, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        if not file_exists:
            writer.writeheader()

        for c in result.get("courses", []):
            times = c.get("上課時間", [])
            time_str = ", ".join(times) if isinstance(times, list) else str(times or "")

            required_en = type_map.get(c.get("必選修"), c.get("必選修", ""))

            writer.writerow({
                "course_code":  c.get("課程代碼", ""),
                "time":         time_str,
                "course_name":  c.get("課名", ""),
                "credits":      c.get("學分", ""),
                "college_code": college_code,
                "dept_code":    dept_code,
                "grade":        degree_label,
                "required":     required_en,
            })


def force_switch_to_english(driver, wait: WebDriverWait) -> bool:
    """
    直接把頁面切到英文（不改你的輸出格式，只是讓頁面結構穩定好 parse）
    回傳 True/False 表示是否切換成功
    """

    try:
        driver.execute_script("if (typeof setLang === 'function') { setLang('eng'); }")
        # wait pages
        wait.until(lambda d: "ENGLISH" in d.page_source or "Credits" in d.page_source or "Elective" in d.page_source)
        return True
    except Exception:
        pass

    # support
    xpaths = [
        "//a[contains(@onclick,\"setLang('eng')\")]",
        "//span[normalize-space()='ENGLISH']/ancestor::a[1]",
    ]
    for xp in xpaths:
        try:
            el = wait.until(EC.element_to_be_clickable((By.XPATH, xp)))
            el.click()
            wait.until(lambda d: "Credits" in d.page_source or "Elective" in d.page_source or "Required" in d.page_source)
            return True
        except Exception:
            pass

    return False
    
def course_info_tool(college: str, dept: str, degree: str, headless: bool = True):
    print(college + "," + dept + ","  + degree)
    """
    - success：return clean str
    - fail ：return "Course tool error: ..."
    """
    try:
        col_code, dept_no = map_to_codes(college, dept)
        degree_label = normalize_degree(degree)
        result = _query_once(col=col_code, dept_no=dept_no, degree_label=degree_label, headless=headless)
        csv_path = get_data_path("CourseInfo.csv")
        
        if result.get("ok"):
            write_courses_to_csv(
                result=result,
                csv_path=csv_path,
                college_code=col_code,
                dept_code=dept_no,
                degree_label=degree_label,
            )

        return _format_clean(result)

    except Exception as e:
        return f"Course tool error: {str(e)}"