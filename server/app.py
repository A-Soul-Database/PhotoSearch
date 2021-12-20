from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import main
import os
import base64
import video_Down
from threading import Thread
import time
import shutil
from git import Repo

UPLOAD_FOLDER = 'tmp'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
TOKEN ="*************************"
app = Flask(__name__)
app.host = '0.0.0.0'
app.port = 9000
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.debug = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
LASTUPDATE = ""


@app.route('/')
def index():
    return render_template('index.html',Last_Update_Info=LASTUPDATE)


@app.route('/search', methods=['POST'])
def Search():
    uploadfile = request.files['file']
    filename = secure_filename(uploadfile.filename)
    uploadfile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    result = str(main.Search().ultraSearch(f"{app.config['UPLOAD_FOLDER']}/{filename}")).replace("'", '"')
    os.remove(f"{app.config['UPLOAD_FOLDER']}/{filename}")
    result = base64.b64encode(result.encode('utf-8'))
    return render_template('result.html', result=str(result, 'utf-8'))

@app.route('/addItem', methods=['GET'])
def AddItem():
    if request.args.get('token') != TOKEN:
        return "Invalid token",403
    if request.args.get('bv') == None:
        return "Invalid bv",403
    t = Thread(target=addItemBackGround, args=(request.args.get('bv'),))
    t.start()
    return "add to list",200

@app.route('/checkUpdate', methods=['GET'])
def CheckUpdate():
    return LASTUPDATE,200

def addItemBackGround(bv)->bool:
    global LASTUPDATE
    Status = video_Down.down(bv)
    if Status:
        main.HashListGen().CaucalateAll()
        os.remove(f"{app.config['UPLOAD_FOLDER']}/{bv}.mp4")
        shutil.copy(os.getcwd()+"/alphas",os.getcwd()+"../"+"alphas")
        LASTUPDATE = f"Trigger {bv} Success \n {time.ctime()}"
        repo = Repo(os.getcwd()+"../")
        repo.commit(f"add new video {bv} By Server Trigger")
        repo.remote().push()
    return "ok"

if __name__ == '__main__':
    app.run(host=app.host, port=app.port)