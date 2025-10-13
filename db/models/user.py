from datetime import datetime
from typing import Optional

from flask import url_for
from flask_login import UserMixin
from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from db import db

class User(db.Model, UserMixin):
    id: Mapped[int] = mapped_column(primary_key = True)
    created: Mapped[datetime] = mapped_column(default = func.now())
    avatar_name: Mapped[str] = mapped_column(default = 'avatar.png')

    name: Mapped[str] = mapped_column(String(length = 20), nullable = False, unique = True)
    mail: Mapped[str] = mapped_column(nullable = True, unique = True)
    password: Mapped[str] = mapped_column(String(length = 128), nullable = False)
    posts: Mapped[list['Post']] = relationship('Post', back_populates = 'author')

    @validates('mail', 'password')
    def validate_user(self, key: str, value: str) -> Optional[str]:
        if not value:
            return None

        return value

    @property
    def avatar(self) -> str:
        return url_for('Account.avatar_page', filename = self.avatar_name)

    @property
    def profile_url(self) -> str:
        return url_for('Account.profile_page', user_id = self.id)

    @property
    def username(self) -> str:
        return f'@{self.name}'
