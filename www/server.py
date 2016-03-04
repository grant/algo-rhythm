import backend as back
import os, threading
from flask import Flask, request, redirect
from flask import jsonify
from flask import render_template
from flask import send_from_directory
from werkzeug.utils import secure_filename


#Move these constants here
BACKEND_BASE = '../dummycode'
UPLOAD_DIR = BACKEND_BASE + '/training_xml_web/'
CONFIG_DIR = BACKEND_BASE + '/trained_configs/'
GENERATED_SONG_DIR = BACKEND_BASE + '/generated_music/'
SCRIPT_ROOT = BACKEND_BASE

backend = back.Backend(UPLOAD_DIR, CONFIG_DIR, GENERATED_SONG_DIR, SCRIPT_ROOT)

UPLOAD_FOLDER = UPLOAD_DIR
CONFIG_FOLDER = CONFIG_DIR
GENERATED_SONG_FOLDER = GENERATED_SONG_DIR
ALLOWED_EXTENSIONS = {'xml'}

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

#Internally, backend can deliver process
#events on multiple threads (with the
#qualification that there is only one
#thread per process), ideally somehow
#process events should be translated
#into notifications to the web browser.
#Do the events need to be synchronized?
#If so, we can set up a central lock
#like this and use it for synchronization.
#In the code as it is now, we will have
#process event notifications print to
#stdout, note that the synchronization
#will guarantee that there will never
#be interleaving of process event printouts,
#however they *can* interleave with
#print output that comes from other
#sources.
#We could also move the lock inside of
#backend, but that would be useless if
#the event delivery threads need to be
#synchronized with other threads as well.
#In any case, hopefully this is enough
#to get started...
processHandlerLock = threading.Lock()

# Setup routes

# Home
# /?animate=false Turns animation off
@app.route('/')
def home():
    # By default loads the animation
    animate = request.args.get('animate') != 'false'

    status = backend.get_status()
    trainingconfigs = [{
            'name': 'file 3',
            'progress': 50,
        }, {
            'name': 'file 4',
            'progress': 10,
        }]
    trainingconfigs = status['training_configs']
    trainedconfigs = ['config1', 'config2']
    trainedconfigs = status['trained_configs']
    generationprocesses=[
            {
                'name': 'file 3',
                'progress': 50,
            }, {
                'name': 'file 4',
                'progress': 10,
            }
        ]
    generationprocesses = status['generating_songs']
    generatedmusic = [{
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
    generatedmusic = status['generated_songs']
    music_files=status['music_files']
    return render_template(
        'index.html',
        animate=animate,
        music_files=music_files,
        trainingconfigs=trainingconfigs,
        trainedconfigs=trainedconfigs,
        generationprocesses=generationprocesses,
        generatedmusic=generatedmusic
    )


# About
@app.route('/about')
def about():
    return render_template('about.html')


# Upload new file
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

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
    status = backend.get_status()
    currentlyTrained = status['trained_configs']
    currentlyTraining = [training['name'] for training in status['training_configs']]
    if len(files) == 0:
        raise RuntimeError('No files checked')
    if name in currentlyTrained:
        raise RuntimeError('Config with that name already exists')
    if name in currentlyTraining:
        raise RuntimeError('Config with that name is being trained')

    ###################### HANDLING OF TRAINING PROCESS EVENTS HERE ############################

    def handleProgressChange(newPercentDone):
      processHandlerLock.acquire()
      print "Progress changed for training process {} to {}%".format(name, newPercentDone)
      processHandlerLock.release()

    def handleTermination():
      processHandlerLock.acquire()
      print "Training process {} terminated!!!!".format(name)
      processHandlerLock.release()

    ######################   (can we send updates to the browser?)   ############################

    # Create the new training process
    backend.start_training_process(
        config=name,
        files=files,
        iterations=iterations,
        progressChangeHandler=handleProgressChange,
        terminationHandler=handleTermination
    )
    return redirect('/?animate=false')


# Generate music
@app.route('/generate', methods=['POST'])
def generate_music():
    config_file = request.form['config']
    length = request.form['length']
    name = request.form['name']

    # Error checking
    status = backend.get_status()
    currentlyGenerated = status['generated_songs']
    currentlyGenerating = [generating['name'] for generating in status['generating_songs']]
    for field in [config_file, length, name]:
        if field is None:
            raise RuntimeError('Field is missing')
    if name in currentlyGenerated:
        raise RuntimeError('song with that name already exists')
    if name in currentlyGenerating:
        raise RuntimeError('song with that name is being generated')

    ###################### HANDLING OF MUSIC GENERATION PROCESS EVENTS HERE ############################

    def handleProgressChange(newPercentDone):
      processHandlerLock.acquire()
      print "Progress changed for generation process for {} to {}%".format(name, newPercentDone)
      processHandlerLock.release()

    def handleTermination():
      processHandlerLock.acquire()
      print "Generation process for {} terminated!!!!".format(name)
      processHandlerLock.release()

    ##########################   (can we send updates to the browser?)   ###############################

    # Create the new generation process
    backend.start_music_generation_process(
        trained_config=config_file,
        song_name=name,
        song_length=length,
        progressChangeHandler=handleProgressChange,
        terminationHandler=handleTermination
    )

    return redirect('/?animate=false')


# View uploaded file
@app.route('/uploads/<name>', methods=['GET', 'POST'])
def view_upload(name=None):
    return send_from_directory(UPLOAD_FOLDER, name)


@app.route('/status', methods=['GET'])
def status():
    return jsonify(**backend.get_status())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
