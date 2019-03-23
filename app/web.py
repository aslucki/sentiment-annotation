import csv
import json
import os
import uuid

from flask import Flask, render_template, request, make_response, url_for


def create_app():
    app = Flask(__name__)
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['UPLOAD_FOLDER'] = 'data'

    return app


def read_data_file(path):
    with open(path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        rows = []
        for row in reader:
            rows.append(row)

    return rows


app = create_app()
data = read_data_file(os.path.join(app.config['UPLOAD_FOLDER'], 'test.csv'))


@app.route('/_check')
def healthcheck():
    return 'OK'


@app.route('/')
def home():
    current_row = increment_counter()
    progress_percentage = round(current_row / len(data) * 100)
    data[current_row][0]

    response =\
        make_response(render_template('home.html',
                                      yt_url=data[current_row][0],
                                      comment=data[current_row][1],
                                      progress=str(progress_percentage) + '%'))
    _set_user_id(response, 'user_id')

    return response


@app.route('/process', methods=['POST'])
def process():

    user_id = _get_user_id(request, 'user_id')
    current_row = increment_counter()

    if current_row < len(data):
        info = request.json
        append_annotaded(info, user_id)
        progress_percentage = round(current_row / len(data) * 100)
        return json.dumps({'yt_url': data[current_row][0],
                           'comment': data[current_row][1],
                           'progress': str(progress_percentage)+'%'})
    else:
        return json.dumps({'yt_url': '',
                           'comment': '',
                           'progress': str(100)+'%'})


def _get_user_id(request: request, cookie_key: str) -> str:

    user_id = request.cookies.get(cookie_key)

    return user_id


def _set_user_id(response, cookie_key: str):

    user_id = request.cookies.get(cookie_key)
    if not user_id:
        user_id = uuid.uuid4().hex[:4]
        response.set_cookie(cookie_key, user_id)

    return response


def increment_counter():
    with open(os.path.join(app.config['UPLOAD_FOLDER'], 'counter.txt'), 'r+') as f:
        number = int(f.read())
        f.seek(0)
        f.write(str(number+1))
        f.truncate()

    return number


def append_annotaded(info, user_id):
    with open(os.path.join(app.config['UPLOAD_FOLDER'], 'annotated.txt'), 'a+') as f:
        annotation = {
            'yt_url': info['yt_url'],
            'comment': info['comment'],
            'label': info['label'],
            'user_id': user_id
        }
        f.write(json.dumps(annotation) + "\n")
