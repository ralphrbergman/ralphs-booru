from flask_wtf import FlaskForm
from wtforms import EmailField, MultipleFileField, PasswordField, SubmitField, StringField, TextAreaField

class LoginForm(FlaskForm):
    username = StringField('username')
    pw = PasswordField('pw')
    submit = SubmitField('submit')

class SignupForm(FlaskForm):
    username = StringField('username')
    email = EmailField('email')
    pw = PasswordField('pw')
    confirm_pw = PasswordField('confirm-pw')
    submit = SubmitField('submit')

class UploadForm(FlaskForm):
    files = MultipleFileField('files')
    directory = StringField('directory')
    op = StringField('op')
    src = StringField('src')
    caption = TextAreaField('caption')
    tags = TextAreaField('tags')
    submit = SubmitField('submit')
