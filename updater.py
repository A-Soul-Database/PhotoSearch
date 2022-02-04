from contextlib import closing
import subprocess
import requests
import main
import json
import os
import time
from zipfile import ZipFile
header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36"}

Remote_Indexer = []
for i in requests.get("https://raw.githubusercontent.com/A-Soul-Database/A-Soul-Data/main/db/main.json").json()["LiveClip"]:
    Remote_Indexer+=requests.get(f"https://raw.githubusercontent.com/A-Soul-Database/A-Soul-Data/main/db/{i}/indexer.json").json()

# Download Latest Released Aplhas
Latest_Release =  requests.get("https://api.github.com/repos/A-Soul-Database/PhotoSearch/releases/latest",headers=header).json()
try:
    Latest_Release = Latest_Release["assets"][0]["browser_download_url"]
except:
    print(Latest_Release)

os.system(f"echo Got Remote Indexer with {len(Remote_Indexer)} items.")

with closing(requests.get(Latest_Release)) as r:
    chunk_size = 10240
    with open("Alphas.zip","wb") as f:
        for chunk in r.iter_content(chunk_size=chunk_size):
            f.write(chunk)

Alphas = ZipFile("Alphas.zip")
Alphas.extractall("./")

Saved_Indexer = []

alphas = [fn for fn in os.listdir("./Alphas") if fn.endswith(".json")]
all = {}
for i in alphas:
    all.update(json.loads(open(f"Alphas/{i}","r",encoding="utf-8").read()))

for _k,_v in all.items():
    name = _v.split(",")[0]
    if "-" in name: name = name.split("-")[0]
    if name not in Saved_Indexer: Saved_Indexer.append(name)
    
Need_To_Update = [fn for fn in Remote_Indexer if fn not in Saved_Indexer]

os.system(f"echo Have {len(Need_To_Update)} items to update.")
# Update Indexer

def getPs(bv):
    r = requests.get("https://api.bilibili.com/x/web-interface/view?bvid="+bv,headers=header).json()
    if r["code"] == -404:
        return []
    return [fn+1 for fn in range(len(r["data"]["pages"])) if "弹幕" not in r["data"]["pages"][fn]["part"]]

for bv in Need_To_Update:
    pages = getPs(bv)
    for ps in pages:
        name = bv if len(pages) == 1 else f"{bv}-{ps}"
        p = subprocess.Popen(f'you-get --debug -O ./{name} --format=dash-flv360 "https://www.bilibili.com/video/{bv}?p={ps}"  >/dev/null 2>&1 ',shell=True)
        p.wait()
        os.system(f"echo {name} Downloaded")


os.system(f"echo {os.listdir('./')}")
main.HashListGen().CaucalateAll()

# Create Release 
os.system(f"echo Creating Release")

env_file = os.getenv('GITHUB_ENV')
times = time.time()
with open(env_file, "a") as f:
    f.write(f"Version={times}")
    f.write("\n")
    f.write(f"Tags={times}")

os.remove("Alphas.zip")
with ZipFile("Alphas.zip","w") as zip:
    for i in os.walk("./Alphas"):
        for j in i[2]:
            zip.write(i[0]+"/"+j)
