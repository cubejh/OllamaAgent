import os
import csv
def get_data_path(filename):
    """get data>(file) path"""
    this_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(this_dir)
    target_dir = os.path.join(project_root, "data")
    os.makedirs(target_dir, exist_ok=True)

    file_path = os.path.join(target_dir, filename)

    if not os.path.exists(file_path):
        if filename.lower() == "coursearrange.csv":
            create_schedule_csv(file_path)
        else:
            with open(file_path, "w", encoding="utf-8") as f:
                pass
    return file_path

def create_schedule_csv(filename="CourseArrange.csv"):
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    periods = [str(i) for i in range(10)] + ["A", "B", "C", "D"]

    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["Period"] + weekdays)
        for p in periods:
            writer.writerow([p] + [""] * len(weekdays))
    print(f"CSV created: {filename}")