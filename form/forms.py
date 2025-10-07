from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired
from wtforms import MultipleFileField, PasswordField
from wtforms.validators import DataRequired, EqualTo

from .fields import StrongPasswordField
from .mixins import EmailMixin, PostMixin, SubmitMixin, StrongPasswordMixin, UsernameMixin, WeakPasswordMixin
from .validators import validate_extension

class LoginForm(FlaskForm, UsernameMixin, WeakPasswordMixin):
    pass

class PostForm(FlaskForm, PostMixin, SubmitMixin):
    pass

class PasswordForm(FlaskForm, WeakPasswordMixin, SubmitMixin):
    new_pw = StrongPasswordField('new_pw')
    confirm_new_pw = StrongPasswordField('confirm_new_pw')

class SignupForm(FlaskForm, EmailMixin, SubmitMixin, StrongPasswordMixin, UsernameMixin):
    confirm_pw = PasswordField('confirm_pw', validators = [
        DataRequired(message = 'You need to confirm your password'),
        EqualTo('pw', message = 'Mismatch between password and confirmation password')
    ])

class UserForm(FlaskForm, EmailMixin, SubmitMixin, WeakPasswordMixin):
    pass

class UploadForm(FlaskForm, PostMixin, SubmitMixin):
    files = MultipleFileField(
        'files',
        validators = [
            FileRequired(),
            validate_extension(['gif', 'jpg', 'jpeg', 'mp4', 'png', 'webm', 'webp'])
        ]
    )

    
