from re import sub
from typing import Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, validates

from db import db
from .mixins.created import CreatedMixin
from .mixins.id import IdMixin
from .mixins.sortable import SortableMixin
from .mixins.serializer import SerializerMixin

MAX_LENGTH = 30
TAG_PATTERN = r'[a-zA-Z0-9-_()]+'  # tag1 tag2 tag3
NEG_PATTERN = TAG_PATTERN.replace('[', '[^')

class Tag(db.Model, CreatedMixin, IdMixin, SortableMixin, SerializerMixin):
    id: Mapped[int] = mapped_column(primary_key = True)
    name: Mapped[str] = mapped_column(
        String(length = MAX_LENGTH),
        nullable = False,
        unique = True
    )
    
    type: Mapped[str] = mapped_column(
        server_default = 'general',
        nullable = False
    )
    desc: Mapped[str] = mapped_column(nullable = True)

    posts: Mapped[list['Post']] = db.relationship(
        back_populates = 'tags',
        secondary = 'tag_association'
    )

    @validates('name')
    def validate_name(self, key: str, value: str) -> Optional[str]:
        """
        Throw ValueError if the tag name isn't up to standard.
        """
        clean = sub(NEG_PATTERN, '', value).strip().lower()

        if not clean:
            raise ValueError('Tag name should be alphanumeric characters '\
            'with underscores, hyphens and opening/closing parenthesis not ' +
            value
            )

        return clean

    @validates('desc')
    def validate_desc(self, key: str, value: str) -> Optional[str]:
        """
        Return None if the description is an empty string.
        """
        value = value.strip()

        if not value:
            return None

        return value

    @property
    def count(self) -> int:
        return len(self.posts)
