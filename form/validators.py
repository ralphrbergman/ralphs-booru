from collections.abc import Sequence

from flask_babel import gettext
from flask_wtf import FlaskForm
from wtforms import Field, ValidationError

def validate_extension(extensions: Sequence[str]):
    def callback(form: FlaskForm, field: Field):
        files = field.data
        if not files:
            return
        
        for file in files:
            filename = file.filename

            if not filename.split('.')[-1] in extensions:
                raise ValidationError(gettext('File type is not acceptable. Acceptable types are: %(extensions)s', extensions = ', '.join(extensions)))

    return callback