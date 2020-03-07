from flaskblog import db, mail
from flask_mail import Message


def send_notification(author, recipients):
    author = db.cx['flaskblog']['users'].find_one({"username": author})
    for recipient in recipients:
        recipient = db.cx['flaskblog']['users'].find_one({"username": recipient})
        message = Message('You have new task to do.',
                      sender='noreply@stropczyk.com',
                      recipients=[recipient['email']])
        message.body = f'''{author['username']} have created a task for you.

Please check the flaskblog app.'''
        mail.send(message)


