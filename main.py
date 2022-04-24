from random import choice

import flask
from flask import Flask, make_response, render_template, request, redirect
from flask_login import login_user, logout_user, login_required, LoginManager, \
    current_user

from forms.register import RegisterForm
from forms.login import LoginForm
from forms.check_word import CheckWordLine

from data.user import User
from data import db_session
from data import pictures

# from config import *
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = "yandexlyceum_secret_key"

login_manager = LoginManager()
login_manager.init_app(app)

# Цвета для игровой таблицы
PLAY_TABLE_COLORS = {
    'right_place': '#345e38',
    'wrong_place': '#786b2e'
}

# Шкала конвертации номера попытки в очки (points)
CONVERT_TRIES_TO_POINTS = {
    1: 10,
    2: 7,
    3: 5,
    4: 3,
    5: 2,
    6: 1
}

# Импорт банка слов для игры
from data.word_bank import WORD_BANK


@app.errorhandler(401)
def unauthorized(error):
    """Обработчик ошибки 401 - Неавторизованный пользователь"""
    return render_template('error.html',
                           error_message='Пожалуйста, зарегистрируйтесь')


@app.errorhandler(500)
def unauthorized(error):
    """Обработчик ошибки 500 - """
    return render_template('error.html',
                           error_message='''Внутренняя ошибка\nЕсли Вам встрет
                           илась эта ошибка, можете обратиться https://t.me/or_redecorate''')


def main():
    db_session.global_init("db/users.db")
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


@app.route('/', methods=['POST', 'GET'])
def start():
    return render_template('main.html')


@app.route('/profile')
def profile_default():
    """ """
    # Если пользователь авторизован, то перенаправляем его на страницу по id
    if current_user.is_authenticated:
        return redirect(f'/profile/{current_user.login}')
    # Иначе - перенаправляем на страницу для регистрации/авторизации
    else:
        return redirect('/login')


@app.route('/profile/<login>', methods=['GET', 'POST'])
@login_required
def profile(login):
    if current_user.is_authenticated:
        user = current_user
    else:
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.login == login).first()
    return render_template('profile.html', user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.login == form.login.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            print('ok')
            return redirect('/')
        return render_template('login.html', form=form,
                               message='Неправильный логин или пароль')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    # Если пользователь нажал на кнопку "Зарегестрироваться"
    if form.validate_on_submit():
        # Проверка на совпадение паролей
        if form.password.data != form.password_again.data:
            return render_template('register.html', form=form,
                                   message="Пароли не совпадают")

        # Проверка на то, что пользователя с таким логином ещё не существует
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.login == form.login.data).first():
            print(db_sess.query(User).filter(
                User.login == form.login.data).first())
            return render_template('register.html', form=form,
                                   message="Пользователь с таким логином уже есть",
                                   )

        user = User(
            name=form.name.data,
            login=form.login.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')

    return render_template('register.html', form=form)


def set_word_and_tries():
    """Получение текущего угадываемого слова и номера попытки для пользователя
    (Если такого слова нет - то получение нового из 'Банка слов')"""
    word = current_user.current_word
    try_number = current_user.current_try

    # Если у пользователя нет текущего угадываемого слова,
    # то случайным образом выбираем новое и обнуляем номер попытки
    if word is None:
        word = choice(WORD_BANK)
        try_number = 0

        db_sess = db_session.create_session()
        user = db_sess.query(User).get(current_user.id)
        user.current_word = word
        user.current_try = 0
        db_sess.commit()
        db_sess.close()


def get_entered_tries():
    """Возвращает табличку с попытками пользователя"""
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(current_user.id)
    db_sess.close()

    words = user.entered_words
    if words is None or words == '':
        words = []
    else:
        words = words.split('~')

    guessed_word = current_user.current_word
    data = [[['-', ''] for i in range(5)] for j in range(6)]
    # Обновляем буквы в таблице попыток
    for row in range(len(words)):
        for column in range(5):
            # Обновляем символ - букву
            data[row][column][0] = words[row][column]
            # Если буква и есть в слове, и на нужном месте - красим в зеленый
            if words[row][column] == guessed_word[column]:
                data[row][column][1] = PLAY_TABLE_COLORS['right_place']
            # Если буква есть, но не на нужном месте - красим в желтый
            elif words[row][column] in guessed_word:
                data[row][column][1] = PLAY_TABLE_COLORS['wrong_place']
    return data


def update_entered_tries(entered_word):
    """Добавляет нововведённое слово в список попыток пользователя"""
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(current_user.id)
    user.current_try += 1
    words = user.entered_words
    if words is None or words == '':
        user.entered_words = entered_word
    else:
        user.entered_words += '~' + entered_word
    db_sess.commit()
    db_sess.close()
    return get_entered_tries()


def try_number_is_over():
    """Проверка на то, что попытка является последней (шестой)"""
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(current_user.id)
    db_sess.close()
    return user.current_try == 6


def right_word(entered_word):
    """Проверка на то, что введённое пользователем слово и есть загаданное"""
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(current_user.id)
    db_sess.close()
    return user.current_word == entered_word


@app.route('/play', methods=['GET', 'POST'])
@login_required
def play():
    """Страница с игрой - угадывание слов"""
    form = CheckWordLine()
    # Получение текущего угадываемого слова
    set_word_and_tries()
    data = get_entered_tries()
    # Если пользователь ввёл слово
    if request.method == 'POST':
        if form.validate_on_submit():

            entered_word = form.word_line.data.lower()
            # Проверка на то, что в введённом слове ровно 5 букв
            if len(entered_word) != 5:
                return render_template('play.html', form=form,
                                       message='В слове должно быть 5 букв')
            data = update_entered_tries(entered_word)

            # Если пользователь отгадал слово
            if right_word(entered_word):
                return player_won(entered_word)
            # Если пользователь превысил кол-во попыток
            if try_number_is_over():
                return player_lost(current_user.current_word)

            # Если пользователь по-прежнему будет отгадывать слово
            form = CheckWordLine()
            return render_template('play.html', data=data, form=form)

    return render_template('play.html', data=data, form=form)


def player_won(word):
    """Функция вызывается в случае выигрыша пользователя"""
    update_points()
    clear_game()
    picture = choice(pictures.HAPPY_PICS)
    return render_template('you_won.html', word=word, picture_link=picture)


def player_lost(word):
    """Функция вызывается в случае проигрыша (превышения количества попыток)"""
    clear_game()
    picture = choice(pictures.SAD_PICS)
    return render_template('game_over.html', word=word, picture_link=picture)


def update_points():
    """Обновляет общий счет у игрока"""
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(current_user.id)
    user.points += CONVERT_TRIES_TO_POINTS[user.current_try]
    user.guessed_count += 1
    db_sess.commit()
    db_sess.close()


def clear_game():
    """Удаляет сведения о текущей игре - количество попыток, загаданное слово
    и список слов-попыток, вводимых пользователем"""
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(current_user.id)
    user.current_word = None
    user.current_try = None
    user.entered_words = None
    db_sess.commit()
    db_sess.close()


@app.route('/top')
@login_required
def top():
    """Страница с отображением топа пользователей"""
    session = db_session.create_session()
    users = session.query(User).all()
    data = [user for user in users]
    return render_template('top.html', users=data)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


if __name__ == '__main__':
    main()
