import csv
import os
import re
from Otools.get_data_path import get_data_path

def parse_time_slot(time_str):
    """
    resolution [5],2~4 or [2],A~C 
    return (weekday_index, list_of_periods)
    """
    print("ts"+time_str)
    match = re.match(r"\[(\d)\],([0-9A-D]+)~([0-9A-D]+)", time_str)
    if not match:
        return None
    weekday = int(match[1]) - 1  # 0=Monday, 4=Friday
    start, end = match[2], match[3]

    periods_order = [str(i) for i in range(10)] + ["A", "B", "C", "D"]
    start_idx = periods_order.index(start)
    end_idx = periods_order.index(end)
    periods = periods_order[start_idx:end_idx+1]
    return weekday, periods

def CSVReader(fileName):
    file_path = get_data_path(fileName)
    with open(file_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        return list(reader)

def CourseReacordSearch(ID,fileName="CourseInfo.csv"):
    coursesInfo = CSVReader(fileName)
    for row in coursesInfo:
        if row and row[0].strip() == ID.strip():
            print("same_"+row[0].strip() + "_"+ID.strip()+"\n")
            return True
        #print("diff"+repr(row[0]), repr(ID))
    return False  

def CourseArrangeSearch(ID, fileName="CourseArrange.csv"):
    coursesInfo = CSVReader(fileName)
    for row in coursesInfo:
        if not row:
            continue
        for cell in row:
            if cell.strip() == ID.strip():
                return True
    return False

def CourseArrangeWrite(ID, fileName="CourseArrange.csv", courseFile="CourseInfo.csv"):
    file_path = get_data_path(fileName)
    course_file_path = get_data_path(courseFile)

    # 讀取課程資訊
    coursesInfo = CSVReader(course_file_path)
    course = None
    for row in coursesInfo:
        if row and row[0].strip() == ID.strip():
            course = row
            break
    print(course)
    if not course:
        print("Course ID not found")
        return False

    # 解析上課時間
    time_slots = course[1].split(",")
    time_slots_parsed = []
    for ts in time_slots:
        parsed = parse_time_slot(ts.strip())
        if parsed:
            time_slots_parsed.append(parsed)

    # 讀取課表
    with open(file_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = list(csv.reader(f))
    
    # 節次對應 CSV 行
    period_row_map = {row[0]: i for i, row in enumerate(reader[1:], 1)}

    # 是否有衝堂
    conflict_flag = False

    # 寫入課表
    for weekday_idx, periods in time_slots_parsed:
        for p in periods:
            row_idx = period_row_map.get(p)
            if row_idx is None:
                continue
            cell = reader[row_idx][weekday_idx + 1].strip()
            if cell != "":
                # 已有課 → 衝堂，append
                reader[row_idx][weekday_idx + 1] = cell + "\n" + ID
                conflict_flag = True
            else:
                reader[row_idx][weekday_idx + 1] = ID

    # 保存 CSV
    with open(file_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(reader)

    return conflict_flag

ID = "F7-106"
print(":::"+ID+":::")
if not CourseReacordSearch(ID):
    print("尚未查詢到此課程")
else:
    if CourseArrangeSearch(ID):
        print("已經存在預排中了")
Conflict = CourseArrangeWrite(ID)
if Conflict:
    print("預排成功，但與現有課程衝突")
else:
    print("預排成功")