from flask_babel import gettext
from flask_wtf.file import FileAllowed
from wtforms import (
    BooleanField,
    EmailField,
    FileField,
    PasswordField,
    RadioField,
    SubmitField,
    StringField,
    TextAreaField
)
from wtforms.validators import DataRequired, Length

from .fields import StrongPasswordField, WeakPasswordField
from .validators import validate_dimensions

class AvatarMixin:
    avatar = FileField('avatar', validators = [
        FileAllowed(
            [
                'gif',
                'jpg',
                'jpeg',
                'png',
                'webp'
            ],
            message = 
            gettext(
                'You can only have a picture as your avatar.'
                '(e.g gif, jpg, jpeg, png or webp)'
            )
        ),
        validate_dimensions()
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
        (1, gettext('User')),
        (2, gettext('Janitor')),
        (8, gettext('Moderator')),
        (10, gettext('Administrator'))
    ],
    coerce = int,
    default = 1)

class SubmitMixin:
    submit = SubmitField('submit')

class StrongPasswordMixin:
    pw = StrongPasswordField('pw')

class OptionalPasswordMixin:
    pw = PasswordField('pw')

class UsernameMixin:
    username = StringField('username', validators = [
        DataRequired(message = gettext('A username is required')),
        Length(
            max = 20,
            message =
            gettext('Usernames can be up to 20 characters in length')
        )
    ])

class WeakPasswordMixin:
    pw = WeakPasswordField('pw')
