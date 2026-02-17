from io import BytesIO
from collections.abc import Callable, Sequence

from flask_babel import gettext
from flask_wtf import FlaskForm
from PIL import Image
from wtforms import Field, ValidationError

Validator = Callable[[FlaskForm, Field], None]

def validate_dimensions(max_width: int = 1000, max_height: int = 1000) -> Validator:
    def callback(form: FlaskForm, field: Field) -> None:
        img_data = field.data

        if not img_data:
            return

        img = Image.open(BytesIO(field.data.read()))
        width, height = img.size

        if width > max_width:
            raise ValidationError(
                gettext(
                    'Width must be less than '\
                    '%(max_width)s pixels, got %(width)s',
                    max_width = max_width,
                    width = width
                )
            )

        if height > max_height:
            raise ValidationError(
                gettext(
                    'Height must be less than '\
                    '%(max_height)s pixels, got %(height)s',
                    max_height = max_height,
                    height = height
                )
            )

    return callback

def validate_extension(extensions: Sequence[str]) -> Validator:
    def callback(form: FlaskForm, field: Field) -> None:
        files = field.data
        if not files:
            return
        
        for file in files:
            filename = file.filename

            if not filename.split('.')[-1] in extensions:
                raise ValidationError(
                    gettext(
                        'File type is not acceptable.'
                        'Acceptable types are: %(extensions)s',
                        extensions = ', '.join(extensions)
                    )
                )

    return callback
