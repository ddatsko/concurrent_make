from flask import Flask, make_response

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploaded_files'


@app.route('/api/v1/<hello>')
def main_page(hello):
    return make_response({'code': 200, 'message': hello})


if __name__ == "__main__":
    app.run()
