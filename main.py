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


@app.route('/search=<params>', methods=['POST', 'GET'])
def search(params):
    if request.method == 'POST':
        return search_word()

    api_server = f'https://owlbot.info/api/v4/dictionary/{params}'
    headers = {'Authorization': 'Token ' + OWL_API_TOKEN}
    response = get_request(api_server, headers=headers)
    owl_api_response = response.json()

    api_server = f'https://imsea.herokuapp.com/api/1?q={params}'
    response = get_request(api_server)
    pics_response = response.json()['results'][:2]

    api_server = f'https://api.dictionaryapi.dev/api/v2/entries/en/{params}'
    response = get_request(api_server)
    dict_api_response = response.json()

    data = [owl_api_response, pics_response, dict_api_response]
    print(data)
    return render_template('search_result.html', title='Результаты поиска',
                           data=data, search=' '.join(params.split('+')))


main()
