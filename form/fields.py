from wtforms import PasswordField
from wtforms.validators import DataRequired, Length

class WeakPasswordField(PasswordField):
    """
    Mixin that provides a password field with DataRequired validator.
    """
    def __init__(self, label = None, validators = None, **kwargs):
        if validators is None:
            validators = list()

        if DataRequired() not in validators:
            validators.insert(0, DataRequired())

        super().__init__(label = label, validators = validators, **kwargs)

class StrongPasswordField(WeakPasswordField):
    def __init__(self, label = None, validators = None, min_len = 8, max_len = 128, **kwargs):
        if validators is None:
            validators = list()

        if not any(isinstance(v, Length) for v in validators):
            validators.append(Length(min = min_len, max = max_len, message = 'Passwords must be from 8 to 128 characters in length'))

        super().__init__(label = label, validators = validators, **kwargs)
