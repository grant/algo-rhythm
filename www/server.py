import backend as back
import os
from flask import Flask, request, redirect
from flask import jsonify
from flask import render_template
from flask import send_from_directory
from werkzeug.utils import secure_filename

backend = back.Backend()

UPLOAD_FOLDER = back.UPLOAD_DIR
CONFIG_FOLDER = back.CONFIG_DIR
GENERATED_SONG_FOLDER = back.GENERATED_SONG_DIR
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


# Setup routes

# Home
# /?animate=false Turns animation off
@app.route('/')
def home():
    # By default loads the animation
    animate = request.args.get('animate') != 'false'

    status = backend.get_status()
    return render_template(
        'index.html',
        animate=animate,
        music_files=status['music_files'],
        trainingconfigs=
        [{
            'name': 'file 3',
            'progress': 50,
        }, {
            'name': 'file 4',
            'progress': 10,
        }],
        trainedconfigs=backend.get_trained_configs(),
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
    if len(files) == 0:
        raise RuntimeError('No files checked')
    if name in backend.get_trained_configs():
        raise RuntimeError('Config with that name already exists')

    # Create the new training process
    backend.start_training_process(
        config=name,
        files=files,
        iterations=iterations,
    )
    return redirect('/?animate=false')


# Generate music
@app.route('/generate', methods=['POST'])
def generate_music():
    config_file = request.form['config']
    length = request.form['length']
    name = request.form['name']

    # Error checking
    for field in [config_file, length, name]:
        if field is None:
            raise RuntimeError('Field is missing')

    # Create the new generation process
    backend.start_music_generation_process(
        trained_config=config_file,
        song_name=name,
        song_length=length,
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
