import os
from flask import Flask
from flask import render_template
from flask import Flask, request, redirect, url_for
from flask import send_from_directory
from werkzeug import secure_filename
from os import listdir
from os.path import isfile, join

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['xml'])

# Setup flask
app = Flask(__name__)
app.debug = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Helper methods
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def get_uploaded_files():
    path = UPLOAD_FOLDER
    files = [{'name': f, 'url': UPLOAD_FOLDER + '/' + f} for f in listdir(path) if isfile(join(path, f))]
    return files

# Setup routes

# Home
@app.route('/')
def home():
    files = get_uploaded_files()
    return render_template('index.html', files=files)

# Upload new file
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect('/')
    elif request.method == 'GET':
        return redirect('/')

# View uploaded file
@app.route('/uploads/<name>', methods=['GET', 'POST'])
def view_upload(name=None):
    return send_from_directory(UPLOAD_FOLDER, name)

if __name__ == '__main__':
    app.run(port=80)
