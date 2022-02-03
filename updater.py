from contextlib import closing
import json
import zipfile
import requests
import main
import os
import time
from zipfile import ZipFile

Remote_Indexer = []
for i in requests.get("https://raw.githubusercontent.com/A-Soul-Database/A-Soul-Data/main/db/main.json").json()["LiveClip"]:
    Remote_Indexer+=requests.get(f"https://raw.githubusercontent.com/A-Soul-Database/A-Soul-Data/main/db/{i}/indexer.json").json()

Saved_Indexer = json.loads(open("indexer.json","r").read())

Need_To_Update = [fn for fn in Remote_Indexer if fn not in Saved_Indexer]

# Download Latest Released Aplhas

with closing(requests.get("https://api.github.com/repos/A-Soul-Database/PhotoSearch/releases/latest").json()["assets"][0]["browser_download_url"]) as r:
    chunk_size = 10240
    with open("Alphas.zip","wb") as f:
        for chunk in r.iter_content(chunk_size=chunk_size):
            f.write(chunk)

Alphas = ZipFile("Alphas.zip")
Alphas.extractall("./")
os.remove("Alphas.zip")

# Update Indexer

def getPs(bv):
    header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36"}
    r = requests.get("https://api.bilibili.com/x/web-interface/view?bvid="+bv,headers=header).json()
    return [fn+1 for fn in range(len(r["data"]["pages"])) if "弹幕" not in r["data"]["pages"][fn]["part"]]

for item in Need_To_Update:
    for ps in getPs(item):
        name = item if len(getPs(item)) == 1 else f"{item}-{ps}"
        Video = os.system(f"you-get -O ./{name} --format=dash-flv360 https://www.bilibili.com/video/{item}?p={ps}")

main.HashListGen().CaucalateAll()

# Create Release

env_file = os.getenv('GITHUB_ENV')
times = time.time()
with open(env_file, "a") as f:
    f.write(f"Version={times}")
    f.write("\n")
    f.write(f"Tags={times}")

with ZipFile("Alphas.zip","w") as zip:
    for i in os.walk("./Alphas"):
        for j in i[2]:
            zip.write(i[0]+"/"+j)