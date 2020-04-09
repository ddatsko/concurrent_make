from flask import Flask, make_response, request, session, send_file
import time
import os
from runner import CommandRunner
from compressor import Compressor

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploaded_files'


@app.route('/api/v1/check')
def main_page():
    return 'OK'


@app.route('/api/v1/build', methods=['POST'])
def build():

    # TODO: Rewrite this peace of SHIT
    f = request.files['file']
    target = f.filename[:-7]
    print(target)
    f.filename = f.filename.split('/')[-1]
    archive_filename = f'{os.getcwd()}/{f.filename}'
    f.save(archive_filename)
    compressor = Compressor('/')
    compressor.extract_files(archive_filename)

    command_runner = CommandRunner(f'{os.getcwd()}/{f.filename[:-7]}')
    commands_file = f"{f.filename[:-7]}.sh"
    output = command_runner.run_commands(commands_file)

    return send_file(f'{archive_filename[:-7]}/{target}', mimetype='application/x-object')


if __name__ == "__main__":
    app.run(port=3000)
