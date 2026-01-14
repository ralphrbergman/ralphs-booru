from datetime import datetime
from enum import Enum
from typing import Optional

from flask import url_for
from flask_login import UserMixin
from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from db import db

class RoleEnum(Enum):
    ADMIN = 'adm'
    MODERATOR = 'mod'
    REGULAR = 'reg'
    TERMINATED = 'ter'

class User(db.Model, UserMixin):
    id: Mapped[int] = mapped_column(primary_key = True)
    created: Mapped[datetime] = mapped_column(default = func.now())
    avatar_name: Mapped[str] = mapped_column(default = 'avatar.png')

    name: Mapped[str] = mapped_column(String(length = 20), nullable = False, unique = True)
    mail: Mapped[str] = mapped_column(nullable = True, unique = True)
    password: Mapped[str] = mapped_column(String(length = 128), nullable = False)

    comments: Mapped[list['Comment']] = relationship('Comment', back_populates = 'author')
    scores: Mapped[list['Score']] = relationship('Score', back_populates = 'user')
    posts: Mapped[list['Post']] = relationship('Post', back_populates = 'author')
    # Defines user's role within the system.
    # Certain users can terminate accounts, delete posts and some can't
    # comment due to restrictions put in place by a moderator.
    role: Mapped[str] = mapped_column(nullable = False, default = 'reg')

    @validates('mail', 'password')
    def validate_user(self, key: str, value: str) -> Optional[str]:
        if not value:
            return None

        return value

    @property
    def avatar(self) -> str:
        return url_for('Account.avatar_page', filename = self.avatar_name)

    @property
    def is_moderator(self) -> bool:
        return self.role == RoleEnum.ADMIN.value or self.role == RoleEnum.MODERATOR.value

    @property
    def profile_url(self) -> str:
        return url_for('Account.profile_page', user_id = self.id)

    @property
    def role_name(self) -> str:
        return RoleEnum(self.role).name.title()

    @property
    def username(self) -> str:
        return f'@{self.name}'
