import json
from pathlib import Path

#path to the directory
DATA_DIR = Path(__file__).resolve().parent.parent/'data'

def load_json(filename: str):
    """
    Load JSON file (user.json, complains.json, municipality.json).
    Returns a Python object (list/dict). If file is empty/missing -> [].
    """
    filepath = DATA_DIR/filename

    if not filepath.exists():
        return []
    
    with open(filepath, "r", encoding = "utf-8") as f:
        try:
            return json.load(f)
        
        except json.JSONDecodeError:
            return [] #if the file has some issue or is empty
        

def save_json(filename:str, data):
    """
    Save Python object into JSON file inside /data directory.
    """

    filepath = DATA_DIR/filename

    with open(filepath, 'w', encoding = 'utf-8') as f:
        json.dump(data,f, indent = 4, ensure_ascii=False)
        