from flask import Flask, make_response, request

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploaded_files'


@app.route('/api/v1/check')
def main_page():
    return 'OK'


@app.route('/api/v1/build', methods=['POST'])
def build():
    f = request.files['file']
    f.save('/home/kumquat/scrapying/concurrent_make/server/hello.tar.xz')
    return '', 200


if __name__ == "__main__":
    app.run(port=3000)
