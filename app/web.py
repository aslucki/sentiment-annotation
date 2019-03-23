import json
import os
import uuid

from flask import Flask, render_template, request, make_response, url_for


def create_app():
    app = Flask(__name__)
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'data')

    return app


def read_data_file(path):
    with open(path, 'r') as f:
        rows = f.readlines()

    return rows


app = create_app()
data = read_data_file(os.path.join(app.config['UPLOAD_FOLDER'], 'dataset_filtered.jsonl'))
data_length = len(data)


@app.route('/_check')
def healthcheck():
    return 'OK'


@app.route('/')
def home():
    current_row = get_counter()

    if current_row < data_length:
        entry = json.loads(data[current_row])
        progress_percentage = round(current_row / data_length * 100, 2)
        response =\
            make_response(render_template('home.html',
                                          yt_url=entry['embed_url'],
                                          comment=entry['comment'],
                                          progress=str(progress_percentage) + '%'))
    else:
        response = \
            make_response(render_template('home.html',
                                          yt_url='',
                                          comment='',
                                          progress='100%'))
    _set_user_id(response, 'user_id')

    return response


@app.route('/process', methods=['POST'])
def process():

    user_id = _get_user_id(request, 'user_id')
    current_row = increment_counter()

    if current_row < data_length:
        info = request.json
        append_annotaded(info, user_id)
        progress_percentage = round(current_row / data_length * 100, 2)

        entry = json.loads(data[current_row])
        return json.dumps({'yt_url': entry['embed_url'],
                           'comment': entry['comment'],
                           'progress': str(progress_percentage)+'%'})
    else:
        info = request.json
        append_annotaded(info, user_id)
        return json.dumps({'yt_url': '',
                           'comment': '',
                           'progress': '100%'})


def _get_user_id(request: request, cookie_key: str) -> str:

    user_id = request.cookies.get(cookie_key)

    return user_id


def _set_user_id(response, cookie_key: str):

    user_id = request.cookies.get(cookie_key)
    if not user_id:
        user_id = uuid.uuid4().hex[:4]
        response.set_cookie(cookie_key, user_id)

    return response


def get_counter():
    with open(os.path.join(app.config['UPLOAD_FOLDER'],
                           'counter.txt'), 'r') as f:
        number = int(f.read())

    return number


def increment_counter():
    with open(os.path.join(app.config['UPLOAD_FOLDER'],
                           'counter.txt'), 'r+') as f:
        number = int(f.read())
        f.seek(0)
        f.write(str(number+1))
        f.truncate()

    return number + 1


def append_annotaded(info, user_id):
    with open(os.path.join(app.config['UPLOAD_FOLDER'],
                           'annotated.jsonl'), 'a+') as f:
        annotation = {
            'yt_url': info['yt_url'],
            'comment': info['comment'],
            'label': info['label'],
            'user_id': user_id
        }

        f.write(json.dumps(annotation) + "\n")
