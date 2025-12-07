import os

def load_api_key(filename="API_key.txt"):
    """
    read API_key.txt and return.
    If file is empty or doesn't exist, throw exception.
    """
    if not os.path.exists(filename):
        raise FileNotFoundError(f"{filename} not found.")

    with open(filename, "r", encoding="utf-8") as f:
        key = f.read().strip()

    if not key:
        raise ValueError("API_key.txt is empty, please check again.")

    return key
