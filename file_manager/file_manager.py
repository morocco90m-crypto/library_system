import json 
from pathlib import Path

class FileManager:
    def __init__(self, folder = "data"):
        self.__folder = Path(folder)
        self.__folder.mkdir(exist_ok=True)

    def save(self, filename, data):
        path = self.__folder / filename
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load(self, filename):
        path = self.__folder / filename
        if not path.exists():
            return []
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)