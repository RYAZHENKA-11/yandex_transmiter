from flask import Flask, url_for, request, render_template, send_from_directory, send_file, redirect
from code_generator import get_code
from first_page_form import FirstForm
from werkzeug.utils import secure_filename
from data import db_session
from data.users import User
from data.files import File
import sqlalchemy

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'dat', 'py', 'mp4', 'mp3'}
db_session.global_init("db/blogs.db")


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


# Главная страница веб приложения. На ней пользователь может перейти на страницы скачивания файла
# или страницу передачи файла. Также есть инструкция, раскрашенная с помощью bootstrap
@app.route('/main', methods=['GET'])
def main():
    return render_template('first_page.html', style=url_for('static', filename='css/style.css'),
                           src=url_for('static', filename='img/razrabi.jpg'))


# Страница передачи файла. На ней пользователь загружает файл на сервер, после чего его переадрусуют на страницу
# с кодом (см. /given)
@app.route('/give', methods=['GET', 'POST'])
def give():
    if request.method == 'POST':
        file = request.files['file']
        file1 = File()
        file1.filename = file.filename

        if file and allowed_file(file.filename):
            while True:
                code = get_code()
                try:
                    file1.code = code

                    db_sess = db_session.create_session()
                    db_sess.add(file1)
                    db_sess.commit()
                    break
                except sqlalchemy.exc.IntegrityError:
                    print('scam_code', code)
            file.save('C:\\Games\\' + code)
            return redirect(f'/given/{code}')
        else:
            return 'формат - кал'

    elif request.method == 'GET':
        return render_template('give_page.html', style=url_for('static', filename='css/style.css'))


# Страница скачивания файла по коду. После скачивания пользователя переадресуют на страницу благодарности
# (см. /downloaded)
@app.route('/download', methods=['POST', 'GET'])
def download():
    form = FirstForm()
    if request.method == 'GET':
        return render_template('get_page.html', style=url_for('static', filename='css/style.css'), form=form)
    elif request.method == 'POST':
        # return redirect('/downloaded')
        db_sess = db_session.create_session()
        for file in db_sess.query(File).filter(File.code == request.form['code']):
            name = file.filename
        try:
            return send_file('C:\\Games\\' + request.form['code'], as_attachment=True, download_name=name)
        except UnboundLocalError:
            return '''Неправильный код. 404 нот фаунд'''


# Страница благодарности за пользование сайтом
@app.route('/downloaded')
def downloaded():
    return render_template('downloaded_page.html', style=url_for('static', filename='css/style.css'),
                           src=url_for('static', filename='img/0000.png'))


# Страница, на которой отображается код, по которому будет скачан загруженный файл.
@app.route('/given/<code>')
def given(code):
    return render_template('given_page.html', style=url_for('static', filename='css/style.css'), code=code,
                           src=url_for('static', filename='img/0000.png'))


# Страница регистрации
@app.route('/', methods=['POST', 'GET'])
def reg():
    if request.method == 'GET':
        return render_template('reg_form.html', style=url_for('static', filename='css/style.css'),
                               src=url_for('static', filename='img/0000.png'))
    elif request.method == 'POST':
        try:
            user = User()
            user.name = request.form['name']
            user.surname = request.form['surname']
            user.email = request.form['email']
            user.login = request.form['login']
            user.hashed_password = request.form['pass']
            db_sess = db_session.create_session()
            db_sess.add(user)
            db_sess.commit()
        except sqlalchemy.exc.IntegrityError:
            return '''Что то пошло не так. Попробуй еще раз..'''
        return redirect('/main')


# Страница логина
@app.route('/login', methods=['POST', 'GET'])
def log():
    if request.method == 'GET':
        return render_template('login_form.html', style=url_for('static', filename='css/style.css'),
                               src=url_for('static', filename='img/0000.png'))
    elif request.method == 'POST':
        db_sess = db_session.create_session()
        for user in db_sess.query(User).filter(User.login == request.form['login']):
            if request.form['pass'] == user.hashed_password:
                return redirect('/main')
        return '''Неверный логин или пароль. Попробуйте еще раз. 418 айм типот'''


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
