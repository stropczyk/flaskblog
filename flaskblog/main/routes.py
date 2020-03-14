from flask import url_for, render_template, Blueprint, request
from flaskblog import db
from flask_pymongo import ASCENDING

main = Blueprint('main', __name__)


@main.route("/")
@main.route("/home", methods=['GET', 'POST'])
def home():
    per_page = 3
    total = db.cx['flaskblog']['posts'].count()
    if request.method == 'GET':
        offset = 0
    if request.method == 'POST':
        old_offset = int(request.form['offset'])
        if 'Next' in request.form:
            offset = old_offset + per_page
            if offset > total:
                offset = old_offset
        elif 'Previous' in request.form:
            offset = old_offset - per_page
            if offset < 0:
                offset = 0

    all_posts = db.cx.flaskblog.posts.find().sort('_id', ASCENDING)
    first_id = all_posts[offset]['_id']

    posts = db.cx.flaskblog.posts.find({'_id': {'$gte': first_id}}).sort('_id', ASCENDING).limit(per_page)

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

    return render_template('home.html', posts=output, offset=offset)


@main.route("/about")
def about():
    return render_template('about.html', title='About')