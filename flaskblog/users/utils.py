import os
import secrets
from PIL import Image
from flask import url_for, current_app
from flask_mail import Message
from flaskblog import mail, db
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_extension = os.path.splitext(form_picture.filename)
    picture_filename = random_hex + f_extension
    picture_path = os.path.join(current_app.root_path, r'static\profile_pics', picture_filename)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_filename


def send_reset_email(user):
    new_user = db.cx['flaskblog']['users'].find_one({"username": user})
    token = get_reset_token(new_user['username'])
    message = Message('Password Reset Request',
                      sender='noreply@stropczyk.com',
                      recipients=[new_user['email']])
    message.body = f'''To reset your password, visit the following link:
{url_for('users.reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(message)


def get_reset_token(user, expires_sec=1800):
    new_user = db.cx['flaskblog']['users'].find_one({"username": user})
    s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
    return s.dumps({'username': new_user['username']}).decode('utf-8')


def verify_reset_token(token):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        username = s.loads(token)['username']
    except:
        return None
    return db.cx['flaskblog']['users'].find_one({"username": username})