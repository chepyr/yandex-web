from flask import Flask, make_response, render_template, request

from config import *

app = Flask(__name__)
app.config['SECRET_KEY'] = FLASK_KEY


def main():
    app.run(port=8080, host='127.0.0.1')


@app.route('/', methods=['POST', 'GET'])
def start():
    if request.method == 'POST':
        print('oks')
        return make_response('okay')

    return render_template('base.html')


main()
