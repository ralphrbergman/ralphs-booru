from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

from .fields import StrongPasswordField, WeakPasswordField

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
