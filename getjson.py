import json

def GetData(key):
    with open("settings.json", "r") as f:
        loadedData = json.load(f)
    return loadedData[key]