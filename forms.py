from collections.abc import Sequence

from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired
from wtforms import EmailField, Field, MultipleFileField, PasswordField, SubmitField, StringField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError

def validate_extension(extensions: Sequence[str]):
    def callback(form: FlaskForm, field: Field):
        files = field.data
        if not files:
            return
        
        for file in files:
            filename = file.filename

            if not filename.split('.')[-1] in extensions:
                raise ValidationError(f'File type is not acceptable. Acceptable types are: {', '.join(extensions)}')

    return callback

class SubmitMixin:
    submit = SubmitField('submit')

class UserMixin:
    username = StringField('username', validators = [
        DataRequired(message = 'A username is required'),
        Length(max = 20, message = 'Usernames can be up to 20 characters in length')
    ])

    pw = PasswordField('pw', validators = [
        DataRequired(message = 'Password is required'),
        Length(min = 8, max = 128, message = 'Password must be from 8 to 128 characters long')
    ])

class LoginForm(FlaskForm, SubmitMixin, UserMixin):
    pass

class SignupForm(FlaskForm, SubmitMixin, UserMixin):
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
