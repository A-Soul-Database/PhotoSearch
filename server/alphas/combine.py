import os
import json
JsonList = [fn for fn in os.listdir("./") if fn.endswith(".json")]
all = {}
for j in JsonList:
    items = json.loads(open(j,'r',encoding='utf-8').read())
    for item in items:
        if all.get(item) is None:
            all.update(json.loads(open(j,'r',encoding='utf-8').read()))
        else:
            all[item] +=',' + items[item]

open("all.json",'w',encoding='utf-8').write(str(all).replace("'",'"'))