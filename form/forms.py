from flask_babel import gettext
from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired
from wtforms import (
    BooleanField,
    FileField,
    IntegerField,
    MultipleFileField,
    PasswordField,
    StringField,
    SelectField,
    TextAreaField
)
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError

from api import get_user_by_username
from .fields import StrongPasswordField
from .mixins import (
    AvatarMixin,
    DeletedMixin,
    EmailMixin,
    OptionalPasswordMixin,
    PostMixin,
    RoleMixin,
    SubmitMixin,
    StrongPasswordMixin,
    UsernameMixin,
    WeakPasswordMixin
)
from .validators import validate_extension

class LoginForm(FlaskForm, UsernameMixin, WeakPasswordMixin):
    remember = BooleanField('remember')

class ManageUserForm(
    FlaskForm,
    EmailMixin,
    OptionalPasswordMixin,
    RoleMixin,
    SubmitMixin,
    UsernameMixin
    ):
    pass

class PostForm(FlaskForm, DeletedMixin, PostMixin, SubmitMixin):
    new_file = FileField('new_file')

class PasswordForm(FlaskForm, WeakPasswordMixin, SubmitMixin):
    new_pw = StrongPasswordField('new_pw')
    confirm_new_pw = StrongPasswordField('confirm_new_pw')

class PostRemovalForm(FlaskForm, SubmitMixin):
    perma = BooleanField('perma')
    reason = StringField(
        'reason',
        validators = [
            Length(
                min = 15,
                max = 150,
                message = 'Reason must be between 15 and 150 characters long.'
            )
        ]
    )

class SearchForm(FlaskForm, SubmitMixin):
    search = StringField('search')

class SignupForm(
    FlaskForm,
    AvatarMixin,
    EmailMixin,
    SubmitMixin,
    StrongPasswordMixin,
    UsernameMixin
    ):
    confirm_pw = PasswordField('confirm_pw', validators = [
        DataRequired(message = gettext('You need to confirm your password')),
        EqualTo(
            'pw',
            message = 
            gettext('Mismatch between password and confirmation password')
        )
    ])

    def validate_username(self, username: str) -> None:
        user = get_user_by_username(username.data)

        if user:
            raise ValidationError(gettext('Username is already taken.'))

class SnapshotForm(FlaskForm, SubmitMixin):
    post_id = IntegerField(
        'post_id',
        validators = (
            DataRequired(
                message = gettext('Please specify which post to search.')
            ),
        )
    )

    class Meta:
        csrf = False

class TagForm(FlaskForm, DeletedMixin, SubmitMixin):
    name = StringField('name', validators = [DataRequired()])
    type = SelectField('type')
    desc = TextAreaField('desc')

class UserForm(
    FlaskForm,
    AvatarMixin,
    EmailMixin,
    SubmitMixin,
    WeakPasswordMixin
):
    pass

class UploadForm(FlaskForm, PostMixin, SubmitMixin):
    files = MultipleFileField(
        'files',
        validators = [
            FileRequired(),
            validate_extension(
                [
                    'gif',
                    'jpg',
                    'jpeg',
                    'mp3',
                    'mp4',
                    'png',
                    'webm',
                    'webp'
                ]
            )
        ]
    )
