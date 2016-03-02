import algorythm_datamodel
import os
from flask import Flask, request, redirect
from flask import jsonify
from flask import render_template
from flask import send_from_directory
from os import listdir
from os.path import isfile, join

datamodel = algorythm_datamodel.AlgorythmDatamodel()

UPLOAD_FOLDER = datamodel.UPLOAD_DIR
CONFIG_FOLDER = datamodel.CONFIG_DIR
GENERATED_SONG_FOLDER = datamodel.GENERATED_SONG_DIR
ALLOWED_EXTENSIONS = set(['xml'])

# Setup flask
app = Flask(__name__)
app.debug = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(CONFIG_FOLDER):
    os.makedirs(CONFIG_FOLDER)
if not os.path.exists(GENERATED_SONG_FOLDER):
    os.makedirs(GENERATED_SONG_FOLDER)


# Helper methods
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def get_uploaded_files():
    path = UPLOAD_FOLDER
    files = [{'name': f, 'url': UPLOAD_FOLDER + '/' + f} for f in listdir(path) if isfile(join(path, f))]
    return files


# Setup routes

# Home
# /?animate=false Turns animation off
@app.route('/')
def home():
    # By default loads the animation
    animate = request.args.get('animate') != 'false'

    return render_template(
        'index.html',
        animate=animate,
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
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    else:
        raise RuntimeError("upload bad file type")
    return redirect('/?animate=false')


# Upload new file
@app.route('/train', methods=['POST'])
def train():
    files = request.form.getlist('file')
    iterations = request.form['iterations']
    name = request.form['name']

    # Error checking
    if len(files) == 0:
        raise RuntimeError('No files checked')
    if name in datamodel.getCompletedTrainedConfigs():
        raise RuntimeError('Config with that name already exists')

    # Create the new training process
    datamodel.startTrainingProcess(
        newProcessName=name,
        targetConfig=name,
        xmlFileList=files,
        numIterations=iterations,
    )
    return redirect('/')


# Generate music
@app.route('/generate', methods=['POST'])
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


@app.route('/status', methods=['GET'])
def status():
    return jsonify(**datamodel.getStatus())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
