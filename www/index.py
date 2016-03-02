import os
from flask import Flask
from flask import render_template
from flask import Flask, request, redirect, url_for
from flask import send_from_directory
from werkzeug import secure_filename
from os import listdir
from os.path import isfile, join

import algorythm_datamodel

datamodel = algorythm_datamodel.AlgorythmDatamodel()

UPLOAD_FOLDER = 'uploads'
CONFIG_FOLDER = 'backend/trained_configs'
ALLOWED_EXTENSIONS = set(['xml'])

# Setup flask
app = Flask(__name__)
app.debug = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(CONFIG_FOLDER):
    os.makedirs(CONFIG_FOLDER)

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
    #files = get_uploaded_files()
    return render_template('index.html',
        files=datamodel.getTrainingFiles(),
        trainingprocesses=
        # datamodel.getTrainingProcessNames(),
        [{
          'name': 'file 3',
          'progress': 50,
        }, {
          'name': 'file 4',
          'progress': 10,
        }],
        trainedconfigs=
        datamodel.getCompletedTrainedConfigs(),
        generationprocesses=[
        {
          'name': 'file 3',
          'progress': 50,
        }, {
          'name': 'file 4',
          'progress': 10,
        }
        ],
        generatedmusic=
        [{
          'name': 'file name 1',
          'tempo': 128,
          'length': '3:02',
        }, {
          'name': 'file name 1',
          'tempo': 128,
          'length': '3:02',
        }, {
          'name': 'file name 1',
          'tempo': 128,
          'length': '3:02',
        }]
    )

# About
@app.route('/about')
def about():
    return render_template('about.html')

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

# Upload new file
@app.route('/train', methods=['POST'])
def train():
    f = request.form
    processName = None
    configName = None
    for key in f.keys():
      #print "Looking at key {}".format(key)
      if key == 'configname':
        l = f.getlist(key)
        if l:
          configName = l[0]
      elif key == 'processname':
        l = f.getlist(key)
        if l:
          processName = l[0]
    if processName == None or configName == None:
      #probably don't do any of the following things, just
      #redirect home, but anyways for now
      raise RuntimeError("process name is None")
    if processName in datamodel.getTrainingProcessNames():
      #invalid process name, we should do something
      pass
    if configName in datamodel.getCompletedTrainedConfigs():
      #this is the name of an existing trained config, invalid, do something
      pass
    if configName in datamodel.getTrainedConfigsInProgress():
      #there is already training happening to a config if this name, invalid, do something
      pass
    #create the new training process
    datamodel.startTrainingProcess(processName, configName, datamodel.getTrainingFiles(), 100) #100 seconds
    return redirect('/')

# Generate music
@app.route('/train', methods=['POST'])
def generate_music():
  # error handling....
  # datamodel.startMusicProcess(processName, configName, seconds, 'backend/trained_music/' + configName)
  return redirect('/')


# View uploaded file
@app.route('/uploads/<name>', methods=['GET', 'POST'])
def view_upload(name=None):
    return send_from_directory(UPLOAD_FOLDER, name)

# View training process log
@app.route('/trainingprocesses/<name>', methods=['GET', 'POST'])
def view_training_process(name=None):
    prefix = "<html><head></head><body><pre>\n"
    postfix = "</pre></body></html>"
    return prefix + datamodel.getOutputForTrainingProcess(name) + postfix

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)


