from flask import Flask, request, send_file, jsonify
import tempfile
import time
import os
from runner import CommandRunner
from compressor import Compressor
from Library import Library, find_libraries
from errors import InvalidLibraryFileName
import json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploaded_files'
app.config['LIBRARIES_DIRECTORIES'] = ['/usr/lib/x86_64-linux-gnu/libfakeroot', '/usr/local/lib',
                                       '/usr/local/lib/x86_64-linux-gnu',
                                       '/lib/x86_64-linux-gnu', '/usr/lib/x86_64-linux-gnu', '/lib32', '/usr/lib32']


@app.route('/api/v1/check')
def main_page():
    return 'OK'


@app.route('/api/v1/libraries', methods=['POST'])
def get_present_libraries():
    present_libraries = []
    print(request.json)
    for library in json.loads(request.json.replace("'", '"'))['needed_libraries']:
        try:
            if Library(library) in app.config['LIBRARIES']:
                present_libraries.append(library)
        except InvalidLibraryFileName:
            continue
    return jsonify({'present_libraries': present_libraries})


@app.route('/api/v1/build', methods=['POST'])
def build():
    # Extracting files
    tempdir = tempfile.TemporaryDirectory()
    print(request.files)

    f = request.files['file']
    commands_file = request.form['commands_file'].strip('/')

    archive_file = tempfile.NamedTemporaryFile(suffix='.tar.xz', dir=tempdir.name)
    archive_filename = archive_file.name.split('/')[-1]

    f.save(archive_file.name)

    compressor = Compressor(tempdir.name)
    compressor.extract_files(archive_filename)
    new_root = f'{tempdir.name}/{archive_filename.split(".")[0]}/'

    archive_file.close()

    # Run commands

    command_runner = CommandRunner(new_root)

    output, code = command_runner.run_commands(commands_file, new_root)
    print(output, code)
    if code != 0:
        response = output, 400
    else:
        # Sending files back
        target_files = [target.strip('/') for target in request.form['targets'].split(', ')]
        compressor.root_path = new_root
        output_file = tempfile.NamedTemporaryFile(suffix='.tar.xz')
        compressor.compress(target_files, output_file.name)
        response = send_file(output_file, mimetype='application/x-object')

    tempdir.cleanup()

    return response


if __name__ == "__main__":
    app.config['LIBRARIES'] = find_libraries(app.config['LIBRARIES_DIRECTORIES'])
    app.run(port=3000)
