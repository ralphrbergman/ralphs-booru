from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, SubmitField, StringField

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
