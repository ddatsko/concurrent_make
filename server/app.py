from flask import Flask, request, send_file, jsonify, make_response, logging
import tempfile
from runner import CommandRunner
from compressor import Compressor
from Library import Library
from errors import InvalidLibraryFileName
import json
from utils import is_password_acceptable, find_libraries
import sys

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploaded_files'
app.config['LIBRARIES_DIRECTORIES'] = ['/usr/lib/x86_64-linux-gnu/libfakeroot', '/usr/local/lib',
                                       '/usr/local/lib/x86_64-linux-gnu',
                                       '/lib/x86_64-linux-gnu', '/usr/lib/x86_64-linux-gnu', '/lib32', '/usr/lib32']


@app.route('/api/v1/check', methods=['POST'])
def main_page():
    try:
        data = json.loads(request.data)
        if is_password_acceptable(data['password']):
            return 'OK'
    except Exception as e:
        # Want to avoid not 200 requests as they will raise an error on the other side
        print(e)
    return 'NOT OK'


@app.route('/api/v1/libraries', methods=['POST'])
def get_present_libraries():
    present_libraries = []
    print(request.json.replace("'", '"'))
    for library in json.loads(request.json.replace("'", '"'))['needed_libraries']:
        try:
            for present_lib in app.config['LIBRARIES']:
                if present_lib >= Library(library):
                    present_libraries.append(library)
        except InvalidLibraryFileName:
            continue
    return jsonify({'present_libraries': present_libraries})


@app.route('/api/v1/all_libraries', methods=['GET', 'POST'])
def all_libraries():
    return jsonify([library.abs_path for library in app.config['LIBRARIES']])


@app.route('/api/v1/get_info', methods=['POST'])
def get_info():
    try:
        data = json.loads(request.data)
        if not is_password_acceptable(data['password']):
            return jsonify({})
        return jsonify({'architecture': CommandRunner.run_one_command('uname -m').strip()})
    except Exception as e:
        print(e)
        return jsonify({})


@app.route('/api/v1/build', methods=['POST'])
def build():
    logger = logging.create_logger(app)
    print(request.form)
    password = request.form['password']
    if not is_password_acceptable(password):
        return make_response('', 400)
    # Extracting files
    tempdir = tempfile.TemporaryDirectory()
    print(request.files)

    f = request.files['file']
    commands_file = request.form['commands_file'].strip('/')

    archive_file = tempfile.NamedTemporaryFile(suffix='.tar.xz', dir=tempdir.name)
    archive_filename = archive_file.name.split('/')[-1]
    print(archive_filename)

    f.save(archive_file.name)

    compressor = Compressor(tempdir.name)
    compressor.extract_files(archive_filename)
    new_root = f'{tempdir.name}/{archive_filename.split(".")[0]}/'

    archive_file.close()

    # Run commands
    print(new_root)

    # TODO> remove this crap []
    command_runner = CommandRunner(new_root + request.form['workdir'].strip('/'), [])

    output, code = command_runner.run_commands(new_root + commands_file, new_root, logger)
    print(output, code)
    if code != 0:
        logger.debug(code)
        response = str(code), 400
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
    # app.config['LIBRARIES'] = find_libraries()
    app.config['LIBRARIES'] = []
    app.run(host='0.0.0.0', port=3000, debug=True, ssl_context='adhoc')
