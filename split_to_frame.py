"""
利用cv每隔一定时间截取一帧并保存
"""
import cv2
import time
import imagehash
from PIL import Image

def main(path:str,intervel:int=30)->bool:
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
                hash = imagehash.phash(Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)),hash_size=16).__str__()
                result[hash] = frame_count/intervel
        else:
            break

    handle = open(f'{path.split(".")[0]}.json','w',encoding='utf-8')
    result = sorted(result.items(),key=lambda d: d[0])
    result = dict(result)
    handle.write(str(result).replace("'",'"'))
    handle.close()
    cap.release()
    print('cost time:',time.time()-time_start)
    return True

main("BV1Hf4y1M7w9.mp4")