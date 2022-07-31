import sys
import os
sys.path.append("../")
import main
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import time
from contextlib import closing
from zipfile import ZipFile
import base64
from threading import Thread
from pydantic import BaseModel

Outer_App = FastAPI()

Outer_App.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
os.path.exists("tmp") or os.mkdir("tmp")

Last_Update = 0


class B64(BaseModel):
    b64: str
class Token(BaseModel):
    token: str
    
def b64_2_img(b64):
    if len(b64) % 3 != 0:
        return b64_2_img(b64+"=")
    try:
        types = b64.split("data:image/")[1].split(";")[0]
    except: raise TypeError("Not A Image")
    content = b64.split(",")[1]
    name = hash(b64)
    with open(f"tmp/{name}.{types}","wb") as f:
        f.write(base64.b64decode(content))
    return name,types

@Outer_App.post("/photo/api/v1/search")
async def search(item: B64):
    """
        Search a photo.
    """
    try:
        name,types = b64_2_img(item.b64)
        result = main.Search().ultraSearch(f"tmp/{name}.{types}")
        os.remove(f"tmp/{name}.{types}")
        return result
    except: return "error"

@Outer_App.post("/photo/api/v1/webhooks/update")
def update(tk:Token):
    """
        Do Update Alpha.
        Only Allow Certain Token.
    """
    try:
        assert os.getenv("Photo_Api_Token") == str(tk.token)
        Thread(target=Do_Update).start()
        return {"code":0,"msg":"Update Start"}
    except: return {"code":1,"msg":"Token Error"}

@Outer_App.get("/photo/api/v1/LastUpdate")
def Get_Last_Update():
    """
        Get Last Update Time.
    """
    return {"code":0,"msg":"ok","data":{"last_update":Last_Update}}

@Outer_App.get("/photo/api/v1/ParseVideo")
def Parse(bv:str,p:int):
    try:
        header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36"}
        Bvinfo = requests.get(f"https://api.bilibili.com/x/web-interface/view?bvid={bv}",headers=header).json()
        cid = Bvinfo["data"]["pages"][p-1]["cid"]
        try:
            playurl = requests.get(f"https://api.bilibili.com/x/player/playurl?bvid={bv}&cid={cid}&otype=json&&platform=html5&high_quality=1",headers=header).json()
        except: return {"code":1,"msg":"Cid Error"}
        return {"code":0,"msg":"ok","data":{"Play_Url":playurl["data"]["durl"][0]["url"],"Title":Bvinfo["data"]["title"]}}
    except Exception as e: return{"code":1,"msg":"Internal Error","error":str(e)}

def Do_Update():
    Start_Time = time.time()
    time.sleep(60)
    Last_Release_Info = requests.get("https://api.github.com/repos/A-Soul-Database/PhotoSearch/releases/latest").json()["assets"][0]["browser_download_url"]
    if time.time()-Start_Time > 300: raise TimeoutError("Timeout")
    
    with closing(requests.get(Last_Release_Info)) as rep:
        chunk_size = 10240
        with open("Alphas.zip","wb") as f:
            for chunk in rep.iter_content(chunk_size=chunk_size):
                f.write(chunk)

    Alphas = ZipFile("Alphas.zip")
    Alphas.extractall("./")
    global Last_Update
    Last_Update = int(time.time())

if __name__ == "__main__":
    import uvicorn
    cpu = os.cpu_count()
    uvicorn.run(app="api:Outer_App",host="localhost",port=5100,workers=cpu)