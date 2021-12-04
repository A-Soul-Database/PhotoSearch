from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import main
import os
import base64

UPLOAD_FOLDER = 'tmp'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.debug = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def Search():
    uploadfile = request.files['file']
    filename = secure_filename(uploadfile.filename)
    uploadfile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    result = str(main.Search().ultraSearch(f"{app.config['UPLOAD_FOLDER']}/{filename}")).replace("'", '"')
    os.remove(f"{app.config['UPLOAD_FOLDER']}/{filename}")
    result = base64.b64encode(result.encode('utf-8'))
    return render_template('result.html', result=str(result, 'utf-8'))


if __name__ == '__main__':
    app.run(5000)