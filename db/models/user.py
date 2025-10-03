from typing import Optional

from flask_login import UserMixin
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, validates

from ..db import db

class User(db.Model, UserMixin):
    id: Mapped[int] = mapped_column(primary_key = True)
    name: Mapped[str] = mapped_column(String(length = 20), nullable = False, unique = True)
    mail: Mapped[str] = mapped_column(nullable = True, unique = True)
    password: Mapped[str] = mapped_column(String(length = 128), nullable = False)

    @validates('mail', 'password')
    def validate_user(self, key: str, value: str) -> Optional[str]:
        if not value:
            return None

        return value

    @property
    def username(self) -> str:
        return f'@{self.name}'
