from flask import url_for, render_template, Blueprint
from flaskblog import db

main = Blueprint('main', __name__)


@main.route("/")
@main.route("/home", methods=['GET', 'POST'])
def home():
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


@main.route("/about")
def about():
    return render_template('about.html', title='About')