import os
import secrets
from datetime import datetime
from flask import render_template, url_for, flash, redirect, request
from flaskblog import app, db, b_crypt
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from flaskblog.models import User
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.cx['flaskblog']['users'].find_one({"username": form.username.data})
        if user and b_crypt.check_password_hash(user['password'], form.password.data):
            user_object = User(username=user['username'], email=user['email'])
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
    posts = db.cx.flaskblog.posts.find()
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


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_extension = os.path.splitext(form_picture.filename)
    picture_filename = random_hex + f_extension
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_filename)
    form_picture.save(picture_path)

    return picture_filename


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            db.save_file(picture_file, form.picture.data)
            db.cx['flaskblog']['users'].update_one(
                {'username': current_user.username},
                {"$set": {'picture': picture_file}}
            )
            current_user.image_file = picture_file
        db.cx['flaskblog']['users'].update_one(
            {'username': current_user.username},
            {"$set": {'username': form.username.data}}
        )
        db.cx['flaskblog']['users'].update_one(
            {'email': current_user.email},
            {"$set": {'email': form.email.data}}
        )
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    user = db.cx['flaskblog']['users'].find_one({"username": current_user.username})
 #   if user['picture']:
  #      image_file = current_user.image_file
   # else:
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        db.cx.flaskblog.posts.insert_one({
            "title": form.title.data,
            "content": form.content.data,
#            "author": current_user,
            "date_posted": datetime.utcnow()
        }
        )
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post', form=form)
