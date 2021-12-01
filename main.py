"""
利用cv每隔一定时间截取一帧并保存
"""
from threading import Thread
import threading
import cv2
import time
import imagehash
from PIL import Image
import distance
import json
import os



Config = {
    "Hash_Size":12,
    "Search_Distance":25,
    "Confidence_Distance":10,
}


def splitDict(m:dict,clips:int)->list:
    """
    将字典按片段分割
    :param m:
    :return:
    """
    new_list = []
    dict_len = len(m)
    # 获取分组数
    while_count = dict_len // clips + 1 if dict_len % clips != 0 else dict_len / clips
    split_start = 0
    split_end = clips
    while(while_count > 0):
        new_list.append({k: m[k] for k in list(m.keys())[split_start:split_end]})
        split_start += clips
        split_end += clips
        while_count -= 1
    return new_list

class Search:

    def ApproxSearch(self):
        """
        已经弃用
        模糊搜索 搜索置信度最大的返回 若达到预设的置信度也返回"""
        start_time = time.time()
        hashinfo = json.loads(open("./All.json","r").read())
        to_search_hash = imagehash.phash(Image.open('12.png'),hash_size=Config["Hash_Size"]).__str__()
        result = {}
        maximumR = ""
        nearestDis = -1
        for i in hashinfo:
            distancse = int(distance.hamming(to_search_hash,i))
            if distancse < nearestDis or nearestDis == -1:
                nearestDis = distancse
                if nearestDis < Config["Search_Distance"]:
                    result[hashinfo[i]]=f"Confidences: {round(1-distancse/len(to_search_hash),2)}"
                    break
                maximumR = hashinfo[i] + f" Confidences: {round(1-nearestDis/len(to_search_hash),2)}"
        print(f"最大准确度：{maximumR},在允许置信度下的结果：{result}")
        print("--- %s seconds ---" % (time.time() - start_time))

    def ultraSearch(self,image:str):
        """
        优化处: 
                1:多线程
                2:分割前两个hash
        """
        start_time = time.time()
        result = {}
        to_search_hash = imagehash.phash(Image.open(f'{image}'),hash_size=Config["Hash_Size"]).__str__()
        hashinfo = json.loads(open(f"alphas/{to_search_hash[:1]}.json","r").read())
        #hashinfo = json.loads(open(f"./All.json","r").read())
        """
        threadLists = []
        threadNum = 2
        def s(hashinfo:dict):
            for i in hashinfo:
                re = {}
                distancse = int(distance.hamming(to_search_hash,i))
                if distancse < Config["Search_Distance"]:
                    #result[hashinfo[i]]=f"Confidences: {round(1-distancse/len(to_search_hash),2)}"
                    re.update({hashinfo[i]:f"Confidences: {round(1-distancse/len(to_search_hash),2)}" })
            result.update(re)

        dicts = splitDict(hashinfo,len(hashinfo)//threadNum)
        for n in range(threadNum):
            t = Thread(target=s,kwargs={"hashinfo":dicts[n]})
            threadLists.append(t)
        
        for t in threadLists:
            t.setDaemon(True)
            t.start()
        for t in threadLists:
            t.join()
        """
        for i in hashinfo:
            distancse = int(distance.hamming(to_search_hash,i))
            if distancse < Config["Search_Distance"]:
                result[hashinfo[i]]=f"Confidences: {round(1-distancse/len(to_search_hash),2)}"
                if distancse < Config["Confidence_Distance"]:
                    break
        
        result= sorted(result.items(), key=lambda d:d[1],reverse=True)
        print(dict(result))
        #print(len(dict(result)))
        print("--- %s seconds ---" % (time.time() - start_time))

class HashListGen:

    def CaucalateAll(self):
        start_time = time.time()
        videoFormat = ["mp4","flv"]
        videoList = [fn for fn in os.listdir(os.getcwd())
            if any(fn.endswith(formats) for formats in videoFormat)
        ]
        for i in videoList:
            self.SlpitSingleVideo(i)
        print(time.time()-start_time)


    def SlpitSingleVideo(self,path:str,intervel:int=30)->dict:
        """
        :param path: 视频文件路径
        :param intervel: 截取帧的时间间隔
        :return:
        """
        time_start = time.time()
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            print("can't open the video")
            raise Exception("can't open the video")
        frame_count = 0
        intervel = int(cap.get(cv2.CAP_PROP_FPS))
        result = {}
        print("Start Capture")
        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                frame_count += 1
                if frame_count % intervel == 0:
                    #符合条件的帧保存
                    #frame_name = os.path.join(os.path.dirname(path),
                    #                          os.path.basename(path).split('.')[0] + '-' + str(frame_count) + '.jpg')
                    #cv2.imwrite(frame_name, frame)
                    #转换当前帧为PIL格式
                    hash = imagehash.phash(Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)),hash_size=Config["Hash_Size"]).__str__()
                    result[hash] = f"{path.split('.')[0]},{frame_count/intervel}"
            else:
                print("Caped")
                break
        result = sorted(result.items(),key=lambda d: d[0])
        result = dict(result)
        self.Seperate_to_Alphas(result)
        #print(sys.getsizeof(result)
        cap.release()
        print(f'{path.split(".")[0]} cost time:',time.time()-time_start)
        return True

    def Seperate_to_Alphas(self,hash:dict):
        """
        把All.json 分割为 A-z 0-9的json
        """
        #All = json.loads(open("./All.json","r").read())
        a = "abcdefghigklmnopqrstuvwxyz0123456789"

        for i in a:
            if os.path.exists(f"alphas/{i}.json"):
                thisdic = json.loads(open(f"alphas/{i}.json","r",encoding="utf-8").read())
            else:
                thisdic = {}
            handle = open(f"alphas/{i}.json","w",encoding="utf-8")
            for j in hash:
                if j[:1] == i:
                    if j in thisdic:
                        #存在哈希值相同的情况
                        thisdic[j] = thisdic[j] + "," + hash[j]
                    else:
                        thisdic.update({j:hash[j]})
            thisdic = sorted(thisdic.items(),key=lambda d:d[0])
            thisdic = dict(thisdic)
            handle.write(str(thisdic).replace("'",'"'))
            handle.close()
#ApproxSearch()
#ApproxSearch()


if __name__ == "__main__":
    import argparse
    import sys
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--calculate", help="calculate all video hash", action="store_true")
    parser.add_argument("-s", "--search", help="search hash", action="store_true")

    if len(sys.argv) == 1:
        print("No arguments")
        sys.exit(1)
    args = parser.parse_args()
    if args.calculate:
        HashListGen().CaucalateAll()
    elif args.search:
        imgs = input("Please input the path you want to search:\n")
        Search().ultraSearch(imgs)