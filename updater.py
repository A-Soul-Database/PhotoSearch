from contextlib import closing
import subprocess
import requests
import main
import json
import os
import time
from zipfile import ZipFile
import downloader
import datetime
import pytz
import shutil

header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36"}
os.system("sudo apt update && apt install -y ffmpeg aria2")
os.system("git clone https://github.com/A-Soul-Database/Asdb-Tools.git 1")
shutil.move("./1/AsdbTools","./AsdbTools")
os.system("sudo pip install -r ./1/requirements.txt")

Remote_Indexer = []
from AsdbTools import Monitors
Remote_Indexer = Monitors.Diff()["data"]
"""
# This Method Get Bvs From Asdb
for i in requests.get("https://raw.githubusercontent.com/A-Soul-Database/A-Soul-Data/main/db/main.json").json()["LiveClip"]:
    Remote_Indexer+=requests.get(f"https://raw.githubusercontent.com/A-Soul-Database/A-Soul-Data/main/db/{i}/indexer.json").json()
"""


os.system(f"echo Got Remote Indexer with {len(Remote_Indexer)} items.")
os.system(f'aria2c -c -s 16 -x 16 -j 16 -k 1M -o ./Alphas.zip "https://github.com/A-Soul-Database/PhotoSearch/releases/download/latest/Alphas.zip"')
os.system("unzip Alphas.zip && rm Alphas.zip")

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

for bv in Need_To_Update:
    try:
        downloader.bilibili(bv,ASDB=True,download_sourcer=0)
    except: ...

os.system(f"echo {os.listdir('./')}")
main.HashListGen().CaucalateAll()

# Create Release 
os.system(f"echo Creating Release")

env_file = os.getenv('GITHUB_ENV')
tz = pytz.timezone('Asia/Shanghai')
date = datetime.datetime.now(tz).strftime("%Y.%m.%d_%H/%M")
with open(env_file, "a") as f:
    f.write(f"Describe=Release_In_{date}(UTC + 8)")
    f.write("\n")

os.system("zip Alphas.zip -r Alphas/*")

# Send Webhooks
try:
    print(requests.post("http://47.93.157.77" , json={"token":os.getenv('APITOKEN')}).json())
except:
    print("Webhook error")
