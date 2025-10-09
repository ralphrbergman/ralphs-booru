from datetime import datetime
from os import getenv
from pathlib import Path
from typing import Any

from flask import url_for
from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from db import db
from .tag_assoc import TagAssociation
from .thumbnail import Thumbnail

CONTENT_PATH = Path(getenv('CONTENT_PATH'))

class Post(db.Model):
    id: Mapped[int] = mapped_column(primary_key = True)
    created: Mapped[datetime] = mapped_column(default = func.now())
    modified: Mapped[datetime] = mapped_column(nullable = True, onupdate = func.now())

    author_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable = False)
    author: Mapped['User'] = relationship(back_populates = 'posts')

    op: Mapped[str] = mapped_column(nullable = True)
    src: Mapped[str] = mapped_column(nullable = True)

    caption: Mapped[str] = mapped_column(nullable = True)
    tags: Mapped[list['Tag']] = db.relationship('Tag', secondary = TagAssociation, backref = 'posts')
    thumbnail: Mapped[Thumbnail] = relationship('Thumbnail', back_populates = 'post')

    # Filesystem attributes.
    directory: Mapped[str] = mapped_column(nullable = True)
    md5: Mapped[str] = mapped_column(nullable = False, unique = True)
    ext: Mapped[str] = mapped_column(String(length = 4), nullable = False)

    # Basic attributes.
    mime: Mapped[str] = mapped_column(nullable = False)
    size: Mapped[int] = mapped_column(nullable = False)

    height: Mapped[int] = mapped_column(nullable = True)
    width: Mapped[int] = mapped_column(nullable = True)

    @validates('caption', 'directory', 'ext', 'md5', 'mime', 'tags')
    def validate_post(self, key: str, value: Any) -> Any:
        if not value:
            return None

        return value

    @property
    def dimensions(self) -> str:
        return f'{self.width}x{self.height}'

    @property
    def name(self) -> str:
        return f'{self.md5}.{self.ext}'

    @property
    def path(self) -> Path:
        return CONTENT_PATH / (self.directory or '') / self.name

    @property
    def view_uri(self) -> str:
        path = url_for('Post.view_file_resource', post_id = self.id)

        return path
