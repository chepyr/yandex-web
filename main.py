from flask import Flask, make_response, render_template, request, redirect
from requests import get as get_request

from config import *

app = Flask(__name__)
app.config['SECRET_KEY'] = FLASK_KEY


def main():
    app.run(port=8080, host='0.0.0.0')


def search_word():
    user_request = request.form.get("search")
    user_request = '+'.join(user_request.split())
    return redirect(f'/search={user_request}')


@app.route('/', methods=['POST', 'GET'])
def start():
    if request.method == 'POST':
        return search_word()

    return render_template('main.html')


@app.route('/profile')
def profile_default():
    """ """
    return redirect(f'/login')
    # # Если пользователь авторизован, то перенаправляем его на страницу по id
    # if ...:
    #     pass
    # # Иначе - перенаправляем на страницу для регистрации/авторизации
    # else:
    #     pass


@app.route('/profile/<int:id>')
def profile(id):
    return make_response(f'User {id}')


@app.route('/login')
def login():
    return make_response(f'login page')


@app.route('/play')
def play():
    return make_response('Play')


@app.route('/top')
def top():
    return make_response(f'Top of users')


main()
