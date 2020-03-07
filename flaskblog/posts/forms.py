from flaskblog import db
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])

    r_text = '''Recipient. [You can add multiple recipients by simply separating them names with a space.]'''

    recipient = StringField(r_text)
    submit = SubmitField('Post')

    def validate_recipient(self, recipient):
        if recipient.data:
            recipients = recipient.data.split(' ')
            for user in recipients:
                user = db.cx['flaskblog']['users'].find_one({"username": user})
                if not user:
                    raise ValidationError("Some user's username is incorrect. Please check and try again.")