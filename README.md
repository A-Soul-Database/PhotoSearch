# PhotoSearch
图像匹配,搜索   
[![Run Daily Check](https://github.com/A-Soul-Database/PhotoSearch/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/A-Soul-Database/PhotoSearch/actions/workflows/main.yml)  
Under developed For asdb 2.0, Core and Auto

![图片.png](https://i.loli.net/2021/12/01/qLroIxYgnQsXPcD.png)  

更新周期: `crontab 0 21 * * *` By Github Actions  

## Api 
Asdb Photo Search Api 现已开放,地址 `https://apihk.asdb.live/photo/api`
- 搜索图片
```json
POST /v1/search

Require
{
  "b64":"data:image/png;base64,iVB.......="
}

Response
{
  "BV1eq4y1G7EU-1,3426.0":"Confidences: 0.78",
  "BV1eq4y1G7EU-1,3430.0":"Confidences: 0.72
}
```
- 最新更新时间
```json
GET /v1/LastUpdate
{"code":0,"msg":"ok","data":{"last_update":0}}
```
- 解析BiliBili播放地址
```json
GET /v1/ParseVideo

Require
Url ?bv= p=

Response
{"code":0,"msg":"ok","data":{"Play_Url":"https://upos-sz-mirr.....0000","Title":"【A-SOUL】乃琳 2022.01.05 您的一周年礼物到啦！点击查收~【直播录像】"}}
```
请勿滥用
