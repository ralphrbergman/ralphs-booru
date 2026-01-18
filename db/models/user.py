from datetime import datetime
from enum import Enum
from typing import Optional

from flask import url_for
from flask_login import UserMixin
from secrets import token_urlsafe
from sqlalchemy import String, func, select
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from db import db
from encryption import bcrypt
from .mixins.serializer import SerializerMixin

def find_user_by_key(key: str) -> Optional[User]:
    """
    Function that returns any user with the provided API key.
    This function is intended to be used in avoiding having
    two or more users to have the same API key.
    """
    return db.session.scalars(
        select(User).where(User._key == key)
    ).first()

class RoleEnum(Enum):
    ADMIN = 'adm'
    MODERATOR = 'mod'
    REGULAR = 'reg'
    TERMINATED = 'ter'

class User(db.Model, UserMixin, SerializerMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if not self.api_key:
            self.api_key = User.generate_key()

    @classmethod
    def generate_key(cls, candidate: Optional[str] = None) -> str:
        """
        Generates a new unique API key.

        Args:
            candidate: Optional already pre-made API key
        """
        if candidate is None:
            candidate = token_urlsafe(32)

        while find_user_by_key(candidate) is not None:
            candidate = token_urlsafe(32)

        return candidate

    id: Mapped[int] = mapped_column(primary_key = True)
    created: Mapped[datetime] = mapped_column(default = func.now())
    avatar_name: Mapped[str] = mapped_column(default = 'avatar.png')

    name: Mapped[str] = mapped_column(String(length = 20), nullable = False, unique = True)
    mail: Mapped[str] = mapped_column(nullable = True, unique = True)
    pw_hash: Mapped[str] = mapped_column(String(length = 255), nullable = False)
    _key: Mapped[str] = mapped_column(String(length = 64), index = True, nullable = False, unique = True)

    comments: Mapped[list['Comment']] = relationship('Comment', back_populates = 'author')
    scores: Mapped[list['ScoreAssociation']] = relationship('ScoreAssociation', back_populates = 'user')
    posts: Mapped[list['Post']] = relationship('Post', back_populates = 'author')
    # Defines user's role within the system.
    # Certain users can terminate accounts, delete posts and some can't
    # comment due to restrictions put in place by a moderator.
    role: Mapped[str] = mapped_column(nullable = False, default = 'reg')

    @validates('mail')
    def validate_user(self, key: str, value: str) -> Optional[str]:
        if not value:
            return None

        return value

    @property
    def avatar(self) -> str:
        return url_for('Root.Account.avatar_page', filename = self.avatar_name)

    @property
    def is_moderator(self) -> bool:
        return self.role == RoleEnum.ADMIN.value or self.role == RoleEnum.MODERATOR.value

    @property
    def api_key(self) -> str:
        return self._key

    @api_key.setter
    def api_key(self, new_key: str):
        self._key = User.generate_key(new_key)

    @property
    def password(self) -> None:
        """ Returns user's password in a hashed form. """
        return self.pw_hash

    @password.setter
    def password(self, password: str):
        if not password or len(password) < 8:
            raise ValueError('Password must be at least 8 characters in length.')

        hashed_password = bcrypt.generate_password_hash(password).decode()
        self.pw_hash = hashed_password

        # Reset user's API key.
        self.api_key = User.generate_key()

    @property
    def profile_url(self) -> str:
        return url_for('Root.Account.profile_page', user_id = self.id)

    @property
    def role_name(self) -> str:
        return RoleEnum(self.role).name.title()

    @property
    def username(self) -> str:
        return f'@{self.name}'

    def check_password(self, other_password: str) -> bool:
        """
        Checks whether the input password is the one stored.

        Args:
            other_password: The password

        Returns:
            bool: Whether the password is correct
        """
        return bcrypt.check_password_hash(self.password, other_password)
