from flask import render_template, url_for, flash, redirect, request
from flaskblog import app, db, b_crypt
from flaskblog.forms import RegistrationForm, LoginForm
from flaskblog.models import User
from flask_login import login_user, current_user, logout_user, login_required


posts = [
    {'author': 'Karol Stropek',
     'title': 'Blog Post 1',
     'content': 'First post content',
     'date_posted': 'January 20, 2020'
    },
    {'author': 'Jane Doe',
     'title': 'Blog Post 2',
     'content': 'Second post content',
     'date_posted': 'January 21, 2020'
    }
]


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.cx['flaskblog']['users'].find_one({"username": form.username.data})
        if user and b_crypt.check_password_hash(user['password'], form.password.data):
            user_object = User(username=user['username'])
            login_user(user_object, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts=posts)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = b_crypt.generate_password_hash(form.password.data).decode('utf-8')
        db.cx.flaskblog.users.insert_one({
            "username": form.username.data,
            "email": form.email.data,
            "password": hashed_password
        }
        )
        flash('Your account has been created! You are now able to log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/account")
@login_required
def account():
    return render_template('account.html', title='Account')