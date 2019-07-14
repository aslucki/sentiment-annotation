import json
import os

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
data = read_data_file(os.path.join(app.config['UPLOAD_FOLDER'], 'dataset_master.jsonl'))
data_length = len(data)


@app.route('/_check')
def healthcheck():
    return 'OK'


@app.route('/')
def info():
    return "Access to the annotation tool requires dedicated id."


@app.route('/annotation/<username>')
def home(username):

    if username not in ["user1", "XIr03", "h5HDF", "master"]:
        return "<h4> User {} is not registered. </h4>".format(username)

    current_row = get_counter(username)
    if current_row < data_length:
        entry = json.loads(data[current_row])
        progress_percentage = round(current_row / data_length * 100, 2)

        if username == "master":
            response =\
                make_response(render_template('master.html',
                                              yt_url=entry['embed_url'],
                                              comment=entry['comment'],
                                              comment_id=entry['comment_id'],
                                              label_1=entry['labels'][0],
                                              label_2=entry['labels'][1],
                                              progress=str(progress_percentage) + '%'))
        else:
            response =\
                make_response(render_template('home.html',
                                              yt_url=entry['embed_url'],
                                              comment=entry['comment'],
                                              comment_id=entry['comment_id'],
                                              progress=str(progress_percentage) + '%'))
    else:
        response = \
            make_response(render_template('home.html',
                                          yt_url='',
                                          comment='',
                                          progress='100%'))

    _set_user_id(response, username, 'user_id')

    return response


@app.route('/annotation/process', methods=['POST'])
def process():

    user_id = _get_user_id(request, 'user_id')
    current_row = increment_counter(user_id)

    if current_row < data_length:
        info = request.json
        append_annotaded(info, user_id)
        progress_percentage = round(current_row / data_length * 100, 2)

        entry = json.loads(data[current_row])
        return json.dumps({'yt_url': entry['embed_url'],
                           'comment': entry['comment'],
                           'comment_id': entry['comment_id'],
                           'label_1': entry['labels'][0],
                           'label_2': entry['labels'][1],
                           'progress': str(progress_percentage)+'%'})
    else:
        info = request.json
        append_annotaded(info, user_id)
        return json.dumps({'yt_url': '',
                           'comment': '',
                           'comment_id': '',
                           'label_1': '',
                           'label_2': '',
                           'progress': '100%'})


@app.route('/stats')
def display_stats():
    with open(os.path.join(app.config['UPLOAD_FOLDER'],
                           'counter.json'), 'r') as f:
        data = json.load(f)

    return render_template('stats.html', data=data)


def get_counter(username):
    with open(os.path.join(app.config['UPLOAD_FOLDER'],
                           'counter.json'), 'r') as f:
        try:
            counter_data = json.load(f)
            number = counter_data.get(username, 0)

        except json.decoder.JSONDecodeError:
            number = 0

    return number


def increment_counter(username):

    with open(os.path.join(app.config['UPLOAD_FOLDER'],
                           'counter.json'), 'r') as f:

        try:
            counter_data = json.load(f)
            number = counter_data.get(username, 0)

        except json.decoder.JSONDecodeError:
            number = 0
            counter_data = {}

    with open(os.path.join(app.config['UPLOAD_FOLDER'],
                            'counter.json'), 'w') as f:

        counter_data[username] = number + 1
        json.dump(counter_data, f)

    return number + 1


def append_annotaded(info, user_id):
    with open(os.path.join(app.config['UPLOAD_FOLDER'],
                           'annotated_final.jsonl'), 'a+') as f:

        annotation = {
            'yt_url': info['yt_url'],
            'comment': info['comment'],
            'label': info['label'],
            'comment_id': info['comment_id'],
            'user_id': user_id
        }

        f.write(json.dumps(annotation) + "\n")


def _get_user_id(request: request, cookie_key: str) -> str:

    user_id = request.cookies.get(cookie_key)

    return user_id


def _set_user_id(response, username, cookie_key: str):

    user_id = request.cookies.get(cookie_key)
    if not user_id or user_id != username:
        response.set_cookie(cookie_key, username)

    return response
