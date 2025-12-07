from readAPI import load_api_key
from ollama_UI import run  

def main():
    api_key = load_api_key()
    run(api_key)

if __name__ == "__main__":
    main()
