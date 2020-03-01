from datetime import datetime
from flask import render_template, url_for, flash, redirect, request, abort, jsonify
from flaskblog import app, db, b_crypt
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, RequestResetForm, \
    ResetPasswordForm
from flaskblog.models import User, save_picture, get_next_sequence
from flask_login import login_user, current_user, logout_user, login_required
from flask_paginate import Pagination, get_page_args
from pymongo import ASCENDING


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
@app.route("/home", methods=['GET', 'POST'])
def home():
    # form = PreviousNextPageForm()
    #
    # offset = 0
    # limit = 5
    #
    # if request.method == 'POST':
    #     if request.form['submit_button'] == 'Next':
    #         offset += limit
    #     elif request.form['submit_button'] == 'Previous':
    #         offset = offset - limit

    # starting_id = db.cx.flaskblog.posts.find().sort('_id', ASCENDING)
    # last_id = starting_id[offset]['_id']

    # posts = db.cx.flaskblog.posts.find({'_id': {'$gte': last_id}}).sort('_id', ASCENDING).limit(limit)
    posts = db.cx.flaskblog.posts.find()

    image_file = url_for('static', filename='profile_pics/' + 'default.jpg')

    output = []

    for post in posts:
        post_author = post['author']
        user = db.cx['flaskblog']['users'].find_one({"username": post_author})
        if user['picture']:
            image_file = user['picture']
        elif user['picture'] is None:
            image_file = 'default.jpg'
        post['image'] = image_file
        output.append({
            '_id': post['_id'],
            'image': post['image'],
            'author': post['author'],
            'date_posted': post['date_posted'],
            'title': post['title'],
            'content': post['content']
        })

    return render_template('home.html', posts=output)


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
            "password": hashed_password,
            "picture": None
        }
        )
        flash('Your account has been created! You are now able to log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


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
    if user['picture']:
        image_file = url_for('static', filename='profile_pics/' + user['picture'])
    else:
        image_file = url_for('static', filename= 'profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        db.cx.flaskblog.posts.insert_one({
            "_id": get_next_sequence("userid"),
            "title": form.title.data,
            "content": form.content.data,
            "author": current_user.username,
            "date_posted": datetime.utcnow()
        }
        )
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post', form=form)


@app.route("/post/<int:post_id>")
def post(post_id):
    single_post = db.cx['flaskblog']['posts'].find_one({"_id": post_id})
    if not single_post:
        abort(404)
    post_author = single_post['author']
    user = db.cx['flaskblog']['users'].find_one({"username": post_author})
    if user['picture']:
        image_file = user['picture']
    elif user['picture'] is None:
        image_file = 'default.jpg'
    single_post['image'] = image_file

    return render_template('post.html', title=single_post['title'],
                           post=single_post, legend='New Post')


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    single_post = db.cx['flaskblog']['posts'].find_one({"_id": post_id})
    if not single_post:
        abort(404)
    if single_post['author'] != current_user.username:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        db.cx['flaskblog']['posts'].update_one(
            {'_id': single_post['_id']},
            {"$set": {'title': form.title.data}}
        )
        db.cx['flaskblog']['posts'].update_one(
            {'_id': single_post['_id']},
            {"$set": {'content': form.content.data}}
        )
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=single_post['_id']))
    elif request.method == 'GET':
        form.title.data = single_post['title']
        form.content.data = single_post['content']
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    single_post = db.cx['flaskblog']['posts'].find_one({"_id": post_id})
    if not single_post:
        abort(404)
    if single_post['author'] != current_user.username:
        abort(403)
    db.cx['flaskblog']['posts'].delete_one(
        {'_id': single_post['_id']}
    )
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))


@app.route("/posts/<string:user>")
def user_posts(user):
    posts = db.cx.flaskblog.posts.find({"author": user})
    if not posts:
        abort(404)
    user = db.cx['flaskblog']['users'].find_one({"username": user})
    image_file = url_for('static', filename='profile_pics/' + 'default.jpg')
    if user['picture']:
        image_file = user['picture']
    elif user['picture'] is None:
        image_file = 'default.jpg'

    output = []
    total = 0
    for post in posts:
        output.append({
            '_id': post['_id'],
            'image': image_file,
            'author': user['username'],
            'date_posted': post['date_posted'],
            'title': post['title'],
            'content': post['content']
        })
        total += 1

    return render_template('user_posts.html', posts=output, user=user, total=total)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))


