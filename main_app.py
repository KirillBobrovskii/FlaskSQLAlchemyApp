from flask import Flask, render_template, request, flash, redirect, session, url_for, abort
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Users

app = Flask(__name__)
app.config['SECRET_KEY'] = 'asdhgajsfaksgkhslahf'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase2.db'

db.init_app(app)

menu = {
    'Главная': '/',
    'Авторизация': '/login'
}


@app.route('/')
def index():
    data = {
        'title': 'Главная',
        'menu': menu
    }
    return render_template('main_app/index.html', data=data)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if 'signed_in' in session:
        return redirect(url_for('account', name=session['signed_in']))
    data = {
        'title': 'Авторизация',
        'menu': menu,
        'button': 'Войти',
        'logup': url_for('logup')
    }
    if request.method == 'POST':
        login = request.form['login']
        result = Users.query.filter(Users.login == login).first()
        if result is not None and check_password_hash(result.password, request.form['password']):
            session['signed_in'] = result.login
            return redirect(url_for('account', name=session['signed_in']))
        else:
            flash('Отказано в доступе!', category='error')
    return render_template('main_app/login.html', data=data)


@app.route('/logup', methods=['POST', 'GET'])
def logup():
    data = {
        'title': 'Регистрация',
        'menu': menu,
        'button': 'Зарегистрироваться'
    }
    if request.method == 'POST':
        login = request.form['login']
        password = generate_password_hash(request.form['password'])
        if login != '' and password != '':
            if Users.query.first() is None:
                user = Users(login=login, password=password)
                db.session.add(user)
                db.session.flush()
                db.session.commit()
                session['signed_in'] = login
                return redirect(url_for('account', name=session['signed_in']))
            else:
                flash('Пользователь уже существует!', category='error')
        else:
            flash('Заполните вся поля формы!', category='error')
    return render_template('main_app/logup.html', data=data)


@app.route('/account/<name>')
def account(name):
    data = {
        'title': 'Личный кабинет',
        'menu': menu,
        'name': name
    }
    if 'signed_in' in session and session['signed_in'] == name:
        return render_template('main_app/account.html', data=data)
    abort(401)


@app.errorhandler(404)
def error404(error):
    data = {
        'title': 'Страница не найдена.',
        'menu': menu
    }
    return render_template('main_app/index.html', data=data)


@app.errorhandler(401)
def error401(error):
    data = {
        'title': 'Ошибка авторизации.',
        'menu': menu
    }
    return render_template('main_app/index.html', data=data)


if __name__ == '__main__':
    app.run(debug=True)
