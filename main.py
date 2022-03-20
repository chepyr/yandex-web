from flask import Flask, make_response

from config import *

app = Flask(__name__)
app.config['SECRET_KEY'] = FLASK_KEY


def main():
    app.run(port=8080, host='127.0.0.1')


@app.route('/')
def start():
    return make_response(f'hello')


main()
