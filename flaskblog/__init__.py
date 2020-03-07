from flask import Flask
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flaskblog.config import Config
import json
import os

db = PyMongo()
b_crypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['SECRET_KEY'] = '3f962c15cca6ee00866c8aa698953946'
    app.config["MONGO_URI"] = \
        "mongodb+srv://guest:stropczyk@database-pjbt9.mongodb.net/flaskblog?retryWrites=true&w=majority"

    db.init_app(app)
    b_crypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from flaskblog.users.routes import users
    from flaskblog.posts.routes import posts
    from flaskblog.main.routes import main
    from flaskblog.errors.handlers import errors
    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(main)
    app.register_blueprint(errors)

    return app


def generate_json_file():
    file_exists = os.path.isfile('flaskblog/posts.json')
    if file_exists:
        pass
    else:
        with open('flaskblog/posts.json', 'w') as f:
            posts = []
            json.dump(posts, f)


def check_json_file():
    posts = db.cx['flaskblog']['posts'].find()
    check_list = []
    for post in posts:
        check_list.append({
            "_id": post['_id'],
            "title": post['title'],
            "content": post['content'],
            "author": post['author']
        })
    with open('flaskblog/posts.json') as file:
        json_list = json.load(file)
    if json_list != check_list:
        json_list = check_list
    with open('flaskblog/posts.json', 'w') as new_file:
        json.dump(json_list, new_file)
