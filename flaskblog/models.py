from flaskblog import db, login_manager


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
