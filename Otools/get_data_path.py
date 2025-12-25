import os

def get_data_path(filename):
    """get data>(file) path"""
    this_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(this_dir)
    target_dir = os.path.join(project_root, "data")
    os.makedirs(target_dir, exist_ok=True)

    file_path = os.path.join(target_dir, filename)

    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            pass
    return file_path