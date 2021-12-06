"""
Bili 视频下载
bv:str 
p:list
qn{
    16: 360P mp4
    32: 480P flv
    64: 720P flv
    ------ 以下需要登录Cookies才能下载
    80: 1080P flv
    116: 1080P60F flv
}
"""
import requests
from contextlib import closing
import logging
import time
import os
class down:

    headers = {
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0",
        "Referer":"https://www.bilibili.com/",
    }

    def __init__(self,bv:str,p:list=[],qn:str="16",path:str="tmp/"):
        self.bv = bv
        self.p = p
        self.qn = qn
        self.path = path
        self.Video_Download(self.Get_Info())
        

    def Get_Info(self)->dict:
        Bili_Video_Info_Api = f"https://api.bilibili.com/x/web-interface/view?bvid={self.bv}"
        Bili_Video_Info_Json = requests.get(Bili_Video_Info_Api,headers=self.headers).json()

        if len(Bili_Video_Info_Json["data"]["pages"]) < len(self.p) or len(self.p)==0:
            #print("请求的分P数大于视频分P数或未指定分P,下载全部分P")
            self.p = [str(i) for i in range(1,len(Bili_Video_Info_Json["data"]["pages"])+1)]
        
        infos = {
            "bv":self.bv,
            "cover":Bili_Video_Info_Json["data"]["pic"],
            "title":Bili_Video_Info_Json["data"]["title"],
            "p":[],
        }
        rolling = self.p[:]
        for i in rolling:
            #循环获得每个分P的信息格式 ["分P","Cid","名字(P1 录播/)"]
            if "弹幕" in Bili_Video_Info_Json["data"]["pages"][int(i)-1]["part"]:
                self.p.remove(i)
            else:
                infos["p"].append([i, Bili_Video_Info_Json["data"]["pages"][int(i)-1]["cid"], Bili_Video_Info_Json["data"]["pages"][int(i)-1]["part"] ])
            #Asdb 特有:去除带有 【弹幕】 的所有分P
        return infos

    def Video_Download(self,infos:dict)->bool:
        result = False
        formats = "mp4" if self.qn == "16" else "flv"
        p = 1
        for i in range(len(infos["p"])):
            url = f"https://api.bilibili.com/x/player/playurl?bvid={infos['bv']}&cid={infos['p'][i][1]}&qn={self.qn}&otype=json"
            Video_Info_Json = requests.get(url,headers=self.headers).json()
            Video_Durl = Video_Info_Json["data"]["durl"][0]["url"]
            name = infos["bv"] if len(infos["p"]) == 1 else f"{infos['bv']}-{str(p)}"
            p+=1
            Video_Name = f"{name}.{formats}"
            #print(Video_Name)
            result = self.Download(Video_Durl,Video_Name)
            
        return result

    def Download(self,url,name)->bool:
        if os.path.exists(name):
            print(f"{name} 已存在")
            return False
        time.sleep(2)
        with closing(requests.session().get(url,headers=self.headers,stream=True)) as response:
            chunk_size = 1024
            with open(f"{self.path}{name}", "wb") as file:
                for data in response.iter_content(chunk_size=chunk_size):
                    file.write(data)
            print(f"{name} 下载完成")
        return True