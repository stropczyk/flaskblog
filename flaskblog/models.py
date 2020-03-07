from flaskblog import db, login_manager
import json


class User:
    def __init__(self, username, email, image_file='default.jpg'):
        self.username = username
        self.email = email
        self.image_file = image_file

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return self.username

    @login_manager.user_loader
    def load_user(username):
        user = db.cx['flaskblog']['users'].find_one({"username": username})
        if user:
            return User(username=user['username'], email=user['email'])


def get_next_sequence(name):
    new_id = db.cx['flaskblog']['counters'].find_and_modify(
        query={"_id": name},
        update={"$inc": {"seq": 1}},
    )
    return new_id['seq']


def add_to_json(task):
    with open('flaskblog/posts.json') as old_file:
        posts = json.load(old_file)
    new_posts = posts
    new_posts.append(task)

    with open('flaskblog/posts.json', 'w') as new_file:
        json.dump(new_posts, new_file)
