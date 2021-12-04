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
        hashinfo = json.loads(open(f"alphas/{to_search_hash[:1]}.json","r").read())
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
        returns = {"op":[],"ed":[]}
        print("Start Recognize")
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
                    """写的很烂 能用就行"""
                    result = Search().ultraSearch(image=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)),type="img")
                    if len(result) != 0:
                        if  len(returns["op"]) == 0 or len(returns["ed"]) == 0:
                            #记录oped的出现时间
                            for i in result.keys():
                                i = i.split(",")
                                for n in i:
                                    if n == "op":
                                        returns["op"].append(int(frame_count/int(cap.get(cv2.CAP_PROP_FPS))))
                                    elif n == "ed":
                                        returns["ed"].append(int(frame_count/int(cap.get(cv2.CAP_PROP_FPS))))
                        else:
                            for i in result.keys():
                                i = i.split(",")
                                for n in i:
                                    if n == "op":
                                        del returns["op"][1]
                                        returns["op"].append(int(frame_count/int(cap.get(cv2.CAP_PROP_FPS))))
                                    elif n == "ed":
                                        del returns["ed"][1]
                                        returns["ed"].append(int(frame_count/int(cap.get(cv2.CAP_PROP_FPS))))
            else:
                print("Caped")
                break
        #print(sys.getsizeof(result)
        """时间好像不是很准确"""
        cap.release()
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

#ApproxSearch()
#ApproxSearch()


if __name__ == "__main__":
    import sys
    print("""
        Asdb Detections
            Useage:
                -c: Check OP/ED
                -t: Check Timeline
                -o: get offset
    """)
    if "-c" in sys.argv:
        print("Check OP/ED")
        name = input("Input the video path: \n")
        result = oped().WhereStarted(name)
        print(result)
    if "-o" in sys.argv:
        print("Check Timeline")
        VidA = input("Input the video A path: \n")
        VidB = input("Input the video B path: \n")
        #DicA = {'op': [1, 1, 2, 2, 3, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 6, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 8, 9, 9, 10, 10, 11, 11, 12, 12, 12, 13, 13, 13, 14, 14, 15, 16, 16], 'ed': [2969, 2979, 2979, 2979, 2979, 2979, 2979, 2979, 2979, 2979, 2980, 2980]}
        #DicB = {'op': [1, 1, 2, 2, 3, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 6, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 8, 9, 9, 10, 10, 11, 11, 12, 12, 12, 13, 13, 13, 14, 14, 15, 16, 16,17], 'ed': [2969, 2979, 2979, 2979, 2979, 2979, 2979, 2979, 2979, 2979, 2980, 2980]}
        OffsetA = oped().WhereStarted(VidA)
        OffsetB = oped().WhereStarted(VidB)
        try:
            OffsetA = OffsetA["op"][-1]
            OffsetB = OffsetB["op"][-1]
            offset = OffsetA - OffsetB
        except:
            #用ed校对
            OffsetA = OffsetA["ed"][0]
            OffsetB = OffsetB["ed"][0]
            offset = OffsetA - OffsetB

        print(f"OffsetA is {OffsetA}\n OffsetB is {OffsetB}\n Offset is {offset}")
        cap = cv2.VideoCapture(VidA)
        videoTime = cap.get(7)/cap.get(5) + offset
        cap.release()
        print(f"Single Offset (A is faster than B) is {offset}, Video Offset is {videoTime}")

    if "-t" in sys.argv:
        import re
        TimeLineA = input("Input the timeline A path: \n")        
        offset = input("Input the offset: default=0 \n")
        TimeLineA = open(TimeLineA,"r",encoding="utf-8").read().split("\n")
        def to_hour(time,offset):
            """秒转换为小时"""
            alltime = 0
            time = time.split(":")
            time.reverse()
            for t in range(len(time)):
                alltime+=int(time[t])*60*t
            alltime-=offset
            #转换秒为小时:分:秒
            return f"{int(alltime/3600)}:{'0'+str(int(alltime%3600/60)) if int(alltime%3600/60)<10 else int(alltime%3600/60)}:{'0'+str(int(alltime%60)) if int(alltime%60)<10 else int(alltime%60)}"
        # 时间轴分割成秒
        newline = []
        timecheck = [r'[0-9]*:[0-9]*',r'[0-9]*:[0-9]*:[0-9]*']
        for i in TimeLineA:
            i = i.replace('：',':')
            for reg in timecheck:
                try:
                    times = re.findall(reg,i)[0]
                    content = re.sub(reg,"",i)
                    newline.append(f"{to_hour(times,offset)}\t{content}")
                except:
                    #错误就先不管了
                    pass
        open("B.txt","w",encoding="utf-8").write("\n".join(newline))
    #HashListGen().CaucalateAll()
