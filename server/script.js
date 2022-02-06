Host = "http://localhost:5100";
Parse_Result = {};
Current_Play = [];
async function Search () {
    let file = document.getElementById("Search_File").files;
    let reader = new FileReader();
    reader.readAsDataURL(file[0]);
    reader.onload = async function (res) {
        let b64 = res.target.result;
        let SearchRequest = new Request(Host + "/api/v1/search" ,{
            method: "POST",
            body : JSON.stringify({"b64": b64}),
            headers: {
                "Content-Type": "application/json"
            },
        })
        let n = await fetch(SearchRequest).then(res=> {
            let result = res.json();
            return result;
        })
        if(n.length == 0) {//if no result
        }
        Parse_Result = n;
        Html = `<ul class="list-group" style="width:autofloat:right">`;
        t = 0;
        for(let k in Parse_Result){
            result= Parse_Bv(k);
            if(t===0){Play_Current(result[0],result[1],result[2])}
            Html+= `<li class="list-group-item" onclick="Play_Current('${result[0]}','${result[1]}','${result[2]}')">${result[0]}中的第${result[2]}秒</li>`
            t+=1
            if(t>10){break}
        }
        Html += `</ul>`;
        document.getElementById("Result").innerHTML = Html;
        document.getElementById("container-index").style.display = "none";
        document.getElementById("container-result").style.display = "block";
}
}

function Get_Play_Url(bv,p){
    Play_Html = `${Host}/api/v1/ParseVideo?bv=${bv}&p=${p}`;
    VUrl = new XMLHttpRequest();
    VUrl.open("GET",Play_Html,false);
    VUrl.send(null);
    res = JSON.parse(VUrl.responseText);
    title = res.data.Title;
    VUrl = res.data.Play_Url;
    return [VUrl,title];
}

function Play_Current(bv,p,time){
    res = Get_Play_Url(bv,p);
    Play_Url = res[0];
    Title = res[1];
    document.getElementById("Video_Title").innerHTML = Title;
    document.getElementById("Index_Video").src = Play_Url+"#t="+time;
    Current_Play = [bv,p,time];
}
function _get_first(Object){
    for(let k in Object){return k}
}
function Parse_Bv(k){
    etc = k.split(",")[0];
    time = k.split(",")[1];
    if(etc.indexOf("-")===-1){bv=etc;p=1}
    else{bv=etc.split("-")[0];p=etc.split("-")[1]}
    return [bv,p,time];
}
function Change_Pages(){
    Status = document.getElementById("container-index").style.display;
    if(Status === "block"){
        document.getElementById("container-index").style.display = "none";
        document.getElementById("container-result").style.display = "block";
    }
    else{
        document.getElementById("container-index").style.display = "block";
        document.getElementById("container-result").style.display = "none";
    }
}
function Jump_Bili(){
    time = parseInt(Current_Play[2]) * 1000;
    Url = `https://www.bilibili.com/video/${Current_Play[0]}?p=${Current_Play[1]}&start_progress=${time}`;
    window.open(Url);
}
function Jump_Asdb(){
    window.open("https://livedb.asoulfan.com/web/index.html#/./list")
}