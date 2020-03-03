import os
import secrets
from PIL import Image
from flaskblog import db, login_manager, app


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


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_extension = os.path.splitext(form_picture.filename)
    picture_filename = random_hex + f_extension
    picture_path = os.path.join(app.root_path, r'static\profile_pics', picture_filename)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_filename


def get_next_sequence(name):
    new_id = db.cx['flaskblog']['counters'].find_and_modify(
        query={"_id": name},
        update={"$inc": {"seq": 1}},
    )
    return new_id['seq']
