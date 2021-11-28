import imagehash
from PIL import Image
import json
import time
import distance

def Way1():
    """
        直接搜索
    """
    start_time = time.time()
    hashinfo = json.loads(open("./BV1Hf4y1M7w9.json","r").read())
    to_search_hash = imagehash.phash(Image.open('far.png'),hash_size=16).__str__()
    result = []
    for i in hashinfo:
        distancse = int(distance.hamming(to_search_hash,i))
        if distancse < 10:
            result.append(hashinfo[i])
            break
    print("--- %s seconds ---" % (time.time() - start_time))
    print(result)

def Way2():
    """
        优化思路:位数切片
    """
    pass

Way1()