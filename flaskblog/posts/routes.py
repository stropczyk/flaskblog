from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from flaskblog import db
from flaskblog.posts.forms import PostForm
from flaskblog.models import get_next_sequence
from datetime import datetime

posts = Blueprint('posts', __name__)


@posts.route("/post/new", methods=['GET', 'POST'])
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
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title='New Post', form=form)


@posts.route("/post/<int:post_id>")
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


@posts.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
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
        return redirect(url_for('posts.post', post_id=single_post['_id']))
    elif request.method == 'GET':
        form.title.data = single_post['title']
        form.content.data = single_post['content']
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')


@posts.route("/post/<int:post_id>/delete", methods=['POST'])
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
    return redirect(url_for('main.home'))