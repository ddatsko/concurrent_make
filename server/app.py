from flask import Flask, make_response, request, session, send_file
import tempfile
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
    tempdir = tempfile.TemporaryDirectory()

    f = request.files['file']
    target_files = request.form['targets']
    commands_file = request.form['commands_file'].strip('/')

    archive_file = tempfile.NamedTemporaryFile(suffix='.tar.xz', dir=tempdir.name)
    archive_filename = archive_file.name.split('/')[-1]

    f.save(archive_file.name)

    compressor = Compressor(tempdir.name)
    compressor.extract_files(archive_filename)
    new_root = f'{tempdir.name}/{archive_filename.split(".")[0]}/'

    archive_file.close()

    command_runner = CommandRunner(new_root)
    print(os.listdir(tempdir.name))
    print(os.listdir(f'{tempdir.name}/{archive_filename.split(".")[0]}/tmp'))
    print(commands_file)

    result_output = command_runner.run_commands(commands_file, new_root)

    print(result_output)



    # target = f.filename[:-7]
    # print(target)
    # f.filename = f.filename.split('/')[-1]
    # archive_filename = f'{os.getcwd()}/{f.filename}'
    # f.save(archive_filename)
    #
    #
    #
    # command_runner = CommandRunner(f'{os.getcwd()}/{f.filename[:-7]}')
    # commands_file = f"{f.filename[:-7]}.sh"
    # output = command_runner.run_commands(commands_file)

    # return send_file(f'{archive_filename[:-7]}/{target}', mimetype='application/x-object')
    return 'hello'


if __name__ == "__main__":
    app.run(port=3000)
