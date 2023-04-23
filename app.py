from flask import Flask, render_template, url_for, request, flash, session, redirect, abort, g, make_response
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import os
from FDataBase import FDataBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from UserLogin import UserLogin

app = Flask(__name__)
app.config.from_object(__name__)
MAX_CONTENT_LENGTH = 2048 * 2048
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Авторизуйтесь для доступа к закрытым страницам"
login_manager.login_message_category = "success"
app.config['SECRET_KEY'] = 'geniy228322'
DATABASE = '/tmp/article.db'
DEBUG = True
SECRET_KEY = 'fdgfh78@#5?>gfhf89dx,v06k'
USERNAME = 'admin'
PASSWORD = '123'

app.config.update(dict(DATABASE=os.path.join(app.root_path,'article.db')))

def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()

@app.route("/")
def index():
    db = get_db()
    dbase = FDataBase(db)
    return render_template('index.html')

@app.route('/car')
def car():
    return render_template('car.html')

@app.route('/car/Toyota')
def toyota():
    return render_template('toyota.html')

@app.route('/car/Mercedes')
def mercedes():
    return render_template('mercedes.html')

@app.route('/car/BMW')
def bmw():
    return render_template('bmw.html')

@app.route('/car/Nissan')
def nissan():
    return render_template('nissan.html')

@app.route('/about')
def about():
    return render_template('abot.html')





def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()


@app.route("/add_post", methods=["POST", "GET"])
def addPost():
    db = get_db()
    dbase = FDataBase(db)

    if request.method == "POST":
        if len(request.form['name']) > 2:
            res = dbase.addPost(request.form['name'], request.form['name_car'], request.form['price'], request.form['felling'])
            if not res:
                flash('Ошибка добавления статьи', category='error')
            else:
                flash('Статья добавлена успешно', category='success')
        else:
            flash('Ошибка добавления статьи', category='error')

    return render_template('Article.html')



@app.route("/tablepost")
def table():
    db = get_db()
    dbase = FDataBase(db)
    return render_template('table.html', posts=dbase.getPostsAnonce())


@app.route("/register", methods=["POST", "GET"])
def register():
    db = get_db()
    dbase = FDataBase(db)

    if request.method == "POST":
        session.pop('_flashes', None)
        if len(request.form['name']) > 2 and len(request.form['login']) > 2 \
                and len(request.form['psw']) > 4 and request.form['psw'] == request.form['psw2']:
            hash = generate_password_hash(request.form['psw'])
            res = dbase.addUser(request.form['name'], request.form['login'], hash)
            if res:
                flash("Вы успешно зарегистрированы", "success")
                return redirect(url_for('login'))
            else:
                flash("Пользователь с таким логином уже существует", "error")
        else:
            flash("Неверно заполнены поля", "error")

    return render_template("register.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for('login'))

@app.route('/profile')
@login_required
def profile():
    db = get_db()
    dbase = FDataBase(db)
    return render_template("profile.html")


@app.route('/userava')
@login_required
def userava():
    img = current_user.getAvatar(app)
    if not img:
        return ""

    h = make_response(img)
    h.headers['Content-Type'] = 'image/png'
    return h


@app.route('/upload', methods=["POST", "GET"])
@login_required
def upload():
    db = get_db()
    dbase = FDataBase(db)
    if request.method == 'POST':
        file = request.files['file']
        if file and current_user.verifyExt(file.filename):
            try:
                img = file.read()
                res = dbase.updateUserAvatar(img, current_user.get_id())
                if not res:
                    flash("Ошибка обновления аватара", "error")
                    return redirect(url_for('profile'))
                flash("Аватар обновлен", "success")
            except FileNotFoundError as e:
                flash("Ошибка чтения файла", "error")
        else:
            flash("Ошибка обновления аватара", "error")

    return redirect(url_for('profile'))

@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    dbase = FDataBase(db)
    print("load_user")
    return UserLogin().fromDB(user_id, dbase)


@app.route("/login", methods=["POST", "GET"])
def login():
    db = get_db()
    dbase = FDataBase(db)
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    if request.method == "POST":
        user = dbase.getUserByEmail(request.form['login'])
        if user and check_password_hash(user['psw'], request.form['psw']):
            userlogin = UserLogin().create(user)
            rm = True if request.form.get('remainme') else False
            login_user(userlogin, remember=rm)
            return redirect(request.args.get("next") or url_for("profile"))

        flash("Неверная пара логин/пароль", "error")

    return render_template("login.html")


@app.route("/post/<int:id_post>")
@login_required
def showPost(id_post):
    db = get_db()
    dbase = FDataBase(db)
    name, name_car, price, feeling = dbase.getPost(id_post)
    if not name:
        abort(404)
    return render_template('post.html', name=name, name_car=name_car, price=price, feeling=feeling)


@app.errorhandler(404)
def pageNotFount(error):
    return render_template('404.html')

if __name__ == "__main__":
    app.run(debug=True)