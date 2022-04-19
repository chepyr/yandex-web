import flask
from flask import Flask, make_response, render_template, request, redirect
from forms.register import RegisterForm
from forms.login import LoginForm
from flask_login import login_user, logout_user, login_required, LoginManager, \
    current_user

from data.user import User
from data import db_session

# from config import *
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = "yandexlyceum_secret_key"

login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db_session.global_init("db/users.db")
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


def search_word():
    user_request = request.form.get("search")
    user_request = '+'.join(user_request.split())
    return redirect(f'/search={user_request}')


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


@app.route('/play')
def play():
    return render_template('play.html')


@app.route('/top')
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
