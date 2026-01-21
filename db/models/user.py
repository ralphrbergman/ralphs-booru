from enum import IntEnum
from os import getenv
from typing import Optional

from flask import url_for
from flask_login import UserMixin
from secrets import token_urlsafe
from sqlalchemy import ForeignKey, Integer, String, func, select
from sqlalchemy.orm import declared_attr, Mapped, column_property, mapped_column, relationship, validates
from sqlalchemy.sql import ColumnElement
from sqlalchemy.ext.hybrid import hybrid_property

from db import db
from encryption import bcrypt
from .comment import Comment
from .mixins.created import CreatedMixin
from .mixins.id import IdMixin
from .mixins.serializer import SerializerMixin
from .post import Post

class RoleEnum(IntEnum):
    ADMIN = 3
    MODERATOR = 2
    REGULAR = 1
    TERMINATED = 0

    @property
    def code(self) -> str:
        return self.name.lower()[:3]

def find_user_by_key(key: str) -> Optional[User]:
    """
    Function that returns any user with the provided API key.
    This function is intended to be used in avoiding having
    two or more users to have the same API key.
    """
    return db.session.scalars(
        select(User).where(User._key == key)
    ).first()

class User(db.Model, CreatedMixin, IdMixin, SerializerMixin, UserMixin):
    LEVEL_HARDNESS = int(getenv('HARDNESS'))

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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if not self.api_key:
            self.api_key = User.generate_key()

    avatar_name: Mapped[str] = mapped_column(default = 'avatar.png')

    name: Mapped[str] = mapped_column(String(length = 20), nullable = False, unique = True)
    mail: Mapped[str] = mapped_column(nullable = True, unique = True)
    pw_hash: Mapped[str] = mapped_column(String(length = 255), nullable = False)
    _key: Mapped[str] = mapped_column(String(length = 64), index = True, nullable = False, unique = True)

    # Relationships.
    comments: Mapped[list['Comment']] = relationship(back_populates = 'author')

    role_id: Mapped[int] = mapped_column(ForeignKey('role.id'))
    role: Mapped['Role'] = relationship(lazy = 'joined')

    snapshots: Mapped[list['Snapshot']] = relationship(back_populates = 'user')
    scores: Mapped[list['ScoreAssociation']] = relationship('ScoreAssociation', back_populates = 'user')
    posts: Mapped[list['Post']] = relationship('Post', back_populates = 'author')

    @validates('mail')
    def validate_user(self, key: str, value: str) -> Optional[str]:
        if not value:
            return None

        return value

    @hybrid_property
    def level(self) -> int:
        s = self.score or 0
        return int(max(0, min(s // self.LEVEL_HARDNESS, 100)))

    @level.expression
    def level(cls):
        return func.cast(cls.score / cls.LEVEL_HARDNESS, Integer)

    @hybrid_property
    def points_until_levelup(self) -> int:
        return User.LEVEL_HARDNESS - (self.score % User.LEVEL_HARDNESS)

    @points_until_levelup.expression
    def points_until_levelup(cls) -> ColumnElement[int]:
        return User.LEVEL_HARDNESS - (cls.score % User.LEVEL_HARDNESS)

    @declared_attr
    def score(cls) -> Mapped[int]:
        return column_property(
            (
                select(func.coalesce(func.sum(Comment.score), 0))
                .where(Comment.author_id == cls.id)
                .correlate_except(Comment)
                .scalar_subquery()
            ) + (
                select(func.coalesce(func.sum(Post.score), 0))
                .where(Post.author_id == cls.id)
                .correlate_except(Post)
                .scalar_subquery()
            )
        )

    @property
    def avatar(self) -> str:
        return url_for('Root.Account.avatar_page', filename = self.avatar_name)

    @property
    def api_key(self) -> str:
        return self._key

    @api_key.setter
    def api_key(self, new_key: str):
        self._key = User.generate_key(new_key)

    @property
    def is_moderator(self) -> bool:
        return self.role >= RoleEnum.MODERATOR

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
    def recent_posts(self) -> list[Post]:
        return tuple(reversed(self.posts))[:10]

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

    def has_permission(self, permission_slug: str) -> bool:
        return any( p.slug == permission_slug for p in self.role.permissions )
