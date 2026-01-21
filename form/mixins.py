from flask_wtf.file import FileAllowed
from wtforms import BooleanField, EmailField, FileField, PasswordField, RadioField, SubmitField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length

from .fields import StrongPasswordField, WeakPasswordField

class AvatarMixin:
    avatar = FileField('avatar', validators = [
        FileAllowed(['gif', 'jpg', 'jpeg', 'png', 'webp'], message = 'You can only have a picture as your avatar. (e.g gif, jpg, jpeg, png or webp)')
    ])

class DeletedMixin:
    deleted = BooleanField('deleted')

class EmailMixin:
    email = EmailField('email')

class PostMixin:
    directory = StringField('directory')
    op = StringField('op')
    src = StringField('src')
    caption = TextAreaField('caption')
    tags = TextAreaField('tags')

class RoleMixin:
    role = RadioField('role', choices = [
        (0, 'Terminated:'),
        (1, 'None:'),
        (2, 'Moderator:'),
        (3, 'Administrator:')
    ],
    default = 'reg')

class SubmitMixin:
    submit = SubmitField('submit')

class StrongPasswordMixin:
    pw = StrongPasswordField('pw')

class OptionalPasswordMixin:
    pw = PasswordField('pw')

class UsernameMixin:
    username = StringField('username', validators = [
        DataRequired(message = 'A username is required'),
        Length(max = 20, message = 'Usernames can be up to 20 characters in length')
    ])

class WeakPasswordMixin:
    pw = WeakPasswordField('pw')
