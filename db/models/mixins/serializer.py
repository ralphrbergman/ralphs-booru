from datetime import datetime
from json import dumps
from inspect import getmembers
from pathlib import Path
from typing import Any

class SerializerMixin:
    # Tuple of attributes to exclude exposure to outside world.
    hidden_attrs = ('path',)

    def to_json(self) -> str:
        data = { c.name: getattr(self, c.name) for c in self.__table__.columns }

        # Include @properties.
        properties = [
            name for name, obj in getmembers(self.__class__)
            if isinstance(obj, property)
        ]

        for prop in properties:
            data[prop] = getattr(self, prop)


        def convert(value: Any) -> Any:
            """
            Function used to convert items between
            types in order to be JSON serializable.
            """
            if hasattr(value, 'to_json'):
                value = value.to_json()

            if isinstance(value, datetime):
                value = value.isoformat()

            if isinstance(value, Path):
                value = str(value)

            return value

        # Deleting from dictionary while iterating solution taken from:
        # https://stackoverflow.com/a/5385075
        for key in list(data.keys()):
            # Exclude sensitive parts before serializing.
            if key in SerializerMixin.hidden_attrs:
                del data[key]
                continue

            data[key] = convert(data[key])

        return dumps(data, indent = 2)
