from flask import Flask, make_response, render_template, request, redirect

from config import *

app = Flask(__name__)
app.config['SECRET_KEY'] = FLASK_KEY


def main():
    app.run(port=8080, host='127.0.0.1')


def search_word():
    user_request = request.form.get("search")
    user_request = '+'.join(user_request.split())
    return redirect(f'/search={user_request}')


@app.route('/', methods=['POST', 'GET'])
def start():
    if request.method == 'POST':
        search_word()

    elif request.method == 'GET':
        return render_template('main.html')


@app.route('/search=<params>', methods=['POST', 'GET'])
def search(params):
    if request.method == 'POST':
        search_word()

    data = params
    return render_template('search_result.html', title='Результаты поиска',
                           data=params)


main()
