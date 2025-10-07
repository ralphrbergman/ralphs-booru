from wtforms import EmailField, SubmitField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length

from .fields import StrongPasswordField, WeakPasswordField

class EmailMixin:
    email = EmailField('email')

class PostMixin:
    directory = StringField('directory')
    op = StringField('op')
    src = StringField('src')
    caption = TextAreaField('caption')
    tags = TextAreaField('tags')

class SubmitMixin:
    submit = SubmitField('submit')

class StrongPasswordMixin:
    pw = StrongPasswordField('pw')

class UsernameMixin:
    username = StringField('username', validators = [
        DataRequired(message = 'A username is required'),
        Length(max = 20, message = 'Usernames can be up to 20 characters in length')
    ])

class WeakPasswordMixin:
    pw = WeakPasswordField('pw')
