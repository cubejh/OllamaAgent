import os

def load_config(filename=".env"):
    """
    Load config file in 'KEY: VALUE' format into a dict.
    Strips leading/trailing spaces from keys and values.
    """
    if not os.path.exists(filename):
        raise FileNotFoundError(f"{filename} not found.")

    config = {}
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue 
            if ":" not in line:
                continue  # 忽略不合法行
            key, value = line.split(":", 1)  
            config[key.strip()] = value.strip()

    return config
