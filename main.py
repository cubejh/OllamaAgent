from readConfig import load_config
from ollama_UI import run  

def main():
    cfg = load_config(".env")
    run(cfg)

if __name__ == "__main__":
    main()

