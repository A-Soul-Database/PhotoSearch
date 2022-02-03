import json
import requests
import main
import os

Remote_Indexer = []
for i in requests.get("https://raw.githubusercontent.com/A-Soul-Database/A-Soul-Data/main/db/main.json").json()["LiveClip"]:
    Remote_Indexer+=requests.get(f"https://raw.githubusercontent.com/A-Soul-Database/A-Soul-Data/main/db/{i}/indexer.json").json()

Saved_Indexer = json.loads(open("indexer.json","r").read())

Need_To_Update = [fn for fn in Remote_Indexer if fn not in Saved_Indexer]

def getPs(bv):
    header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36"}
    r = requests.get("https://api.bilibili.com/x/web-interface/view?bvid="+bv,headers=header).json()
    return [fn+1 for fn in range(len(r["data"]["pages"])) if "弹幕" not in r["data"]["pages"][fn]["part"]]

for item in Need_To_Update:
    for ps in getPs(item):
        name = item if len(getPs(item)) == 1 else f"{item}-{ps}"
        Video = os.system(f"you-get -O ./{name} --format=dash-flv360 https://www.bilibili.com/video/{item}?p={ps}")

main.HashListGen().CaucalateAll()
