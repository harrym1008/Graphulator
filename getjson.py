import json


def GetData(key):
    with open("settings.json", "r") as f:
        loadedData = json.load(f)       # load the JSON file
    return loadedData[key]              # return the data for the key parameter