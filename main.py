from readConfig import load_config
from ollama_UI import run  

def main():
    cfg = load_config(".env")
    run(cfg)

if __name__ == "__main__":
    main()


    """
    1. 
    2. Search(write->csv(ID, Time, CourseName, CoursePt, CourseSC))
     
    3. CSV(ReadCSV,ReadRecord,Search,->Write(return success, fail)->Response)
    4. OpenCSV(Tool)
    5. AddintoCSV
    
    (3) 
    Already Choose(return ...)
    DNE(return ...)
    Conflict(add(0) -> return...)
    Success(add(1) -> return...)
    """

