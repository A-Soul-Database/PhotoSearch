"""
利用cv每隔一定时间截取一帧并保存
"""
import cv2
import time
import imagehash
from PIL import Image
import distance
import json

Config = {
    "Hash_Size":12,
    "Search_Distance":25,
    "Confidence_Distance":10,
    "Ending_Distances":10,
}


class Search:

    def ultraSearch(self,image,type:str="path"):
        """
        优化处: 
                1:多线程
                2:分割前两个hash
            type:
                path: 指定图片路径
                img: 指定图片(PIL 格式)
        """
        start_time = time.time()
        result = {}
        if type == "path":
            to_search_hash = imagehash.phash(Image.open(f'{image}'),hash_size=Config["Hash_Size"]).__str__()
        elif type == "img":
            to_search_hash = imagehash.phash(image,hash_size=Config["Hash_Size"]).__str__()
        hashinfo = json.loads(open(f"opeds/{to_search_hash[:1]}.json","r").read())
        #hashinfo = json.loads(open(f"./All.json","r").read())
        
        for i in hashinfo:
            try:
                distancse = int(distance.hamming(to_search_hash,i))
            except:
                distancse = -1
            if 0< distancse < Config["Search_Distance"]:
                result[hashinfo[i]]=f"Confidences: {round(1-distancse/len(to_search_hash),2)}"
                if distancse < Config["Confidence_Distance"]:
                    break
        
        result= sorted(result.items(), key=lambda d:d[1],reverse=True)
        return dict(result)

class oped(Search):
    """
     检测OP/ED 出现时间
    """

    def WhereStarted(self,path:str):
        """
            OPED的出现时间
        """
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            print("can't open the video")
            raise Exception("can't open the video")
        frame_count = 0
        intervel = int(cap.get(cv2.CAP_PROP_FPS))
        start_time = time.time()
        returns = {"op":[-1,0],"ed":[0,0],"absolute":0}
        print("Start Recognize")
        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                frame_count += 1
                if frame_count % intervel == 0:
                    result = Search().ultraSearch(image=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)),type="img")
                    sec = int(frame_count/int(cap.get(cv2.CAP_PROP_FPS)))
                    if len(result) != 0:
                            #记录oped的出现时间
                        for i in result.keys():
                            i = i.split(",")
                            for n in i:
                                if n == "op":
                                    if returns["op"][0] == -1:
                                        returns["op"][0] = sec
                                    else:
                                        if sec - returns["op"][1] < Config["Ending_Distances"]:
                                            returns["op"][1] = sec
                                elif n == "ed":
                                    if returns["ed"][0] == 0:
                                        returns["ed"][0] = sec
                                    else:
                                        returns["ed"][1] = sec
            else:
                break
        cap.release()
        returns["absolute"] = returns["op"][1] - returns["ed"][0]
        print(time.time()-start_time)
        return returns

    def checkTimeline():
        """
        检测时间轴
                A & A(Timeline)
                B -> B timeline 
            Features :
                1: 检测OP/ED 时间
                2: 
        """
        pass


if __name__ == "__main__":
    name = input("Input the video path: \n")
    result = oped().WhereStarted(name)
    print(result)