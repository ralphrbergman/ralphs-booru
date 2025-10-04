from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired
from wtforms import EmailField, MultipleFileField, PasswordField, StringField, TextAreaField
from wtforms.validators import DataRequired, EqualTo

from .mixins import SubmitMixin, StrongPasswordMixin, UsernameMixin, WeakPasswordMixin
from .validators import validate_extension

class LoginForm(FlaskForm, UsernameMixin, WeakPasswordMixin):
    pass

class SignupForm(FlaskForm, SubmitMixin, StrongPasswordMixin, UsernameMixin):
    email = EmailField('email')
    confirm_pw = PasswordField('confirm_pw', validators = [
        DataRequired(message = 'You need to confirm your password'),
        EqualTo('pw', message = 'Mismatch between password and confirmation password')
    ])

class UploadForm(FlaskForm, SubmitMixin):
    files = MultipleFileField(
        'files',
        validators = [
            FileRequired(),
            validate_extension(['gif', 'jpg', 'jpeg', 'mp4', 'png', 'webm', 'webp'])
        ]
    )

    directory = StringField('directory')
    op = StringField('op')
    src = StringField('src')
    caption = TextAreaField('caption')
    tags = TextAreaField('tags')
