from datetime import datetime
from math import floor, log, pow
from os import getenv
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from flask import url_for
from sqlalchemy import String, func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy.sql import ColumnElement

from db import db
from .thumbnail import Thumbnail
from .mixins.author import AuthorMixin
from .mixins.created import CreatedMixin
from .mixins.id import IdMixin
from .mixins.removed import RemovedMixin
from .mixins.score import ScoreMixin
from .mixins.sortable import SortableMixin
from .mixins.serializer import SerializerMixin

CONTENT_PATH = Path(getenv('CONTENT_PATH'))
NSFW_TAG_NAME = getenv('NSFW_TAG', 'nsfw')
SENSITIVE_DIRS = getenv('SENSITIVE_DIRS', '').split(',')
DISK_SIZES = ('B', 'KB', 'MB', 'GB')

class Post(
    db.Model,
    AuthorMixin,
    CreatedMixin,
    IdMixin,
    RemovedMixin,
    ScoreMixin,
    SortableMixin,
    SerializerMixin
):
    modified: Mapped[datetime] = mapped_column(
        nullable = True,
        onupdate = func.now()
    )

    op: Mapped[str] = mapped_column(nullable = True)
    src: Mapped[str] = mapped_column(nullable = True)

    caption: Mapped[str] = mapped_column(nullable = True)
    tags: Mapped[list['Tag']] = relationship(
        'Tag',
        secondary = 'tag_association',
        back_populates = 'posts'
    )
    thumbnail: Mapped[Thumbnail] = relationship(
        'Thumbnail',
        back_populates = 'post'
    )

    # Filesystem attributes.
    directory: Mapped[str] = mapped_column(nullable = True)
    md5: Mapped[str] = mapped_column(nullable = False, unique = True)
    ext: Mapped[str] = mapped_column(String(length = 4), nullable = False)

    # Basic attributes.
    mime: Mapped[str] = mapped_column(nullable = False)
    size: Mapped[int] = mapped_column(nullable = False)

    height: Mapped[int] = mapped_column(nullable = True)
    width: Mapped[int] = mapped_column(nullable = True)

    comments: Mapped[list['Comment']] = relationship(back_populates = 'post', cascade = 'all, delete-orphan')
    snapshots: Mapped[list['Snapshot']] = relationship(
        back_populates = 'post',
        cascade = 'all, delete-orphan'
    )
    scores: Mapped[list['ScoreAssociation']] = relationship(
        'ScoreAssociation',
        primaryjoin="and_"
        "(Post.id == foreign(ScoreAssociation.target_id)," \
        "ScoreAssociation.target_type == 'post')",
        viewonly=True,
        overlaps="scores"
    )

    @classmethod
    def is_hyperlink(cls, value: str) -> bool:
        url = urlparse(value)
        return any(( url.netloc, url.scheme ))

    @validates(
        'caption',
        'directory',
        'ext',
        'md5',
        'mime',
        'op',
        'src',
        'tags'
    )
    def validate_post(self, key: str, value: Any) -> Any:
        if not value:
            return None

        return value

    @hybrid_property
    def cat(self) -> str:
        return self.mime.split('/')[0] if self.mime else None

    @cat.inplace.expression
    def category(cls) -> ColumnElement[str]:
        return func.substr(
            cls.mime,
            1,
            func.instr(cls.mime, '/') - 1
        )

    @hybrid_property
    def year(self) -> int:
        return self.created.year

    @year.expression
    def year(cls) -> ColumnElement[int]:
        return func.extract('year', cls.created)
    
    @hybrid_property
    def month(self) -> int:
        return self.created.month

    @month.expression
    def month(cls) -> ColumnElement[int]:
        return func.extract('month', cls.created)
    
    @hybrid_property
    def day(self) -> int:
        return self.created.day

    @day.expression
    def day(cls) -> ColumnElement[int]:
        return func.extract('day', cls.created)

    @property
    def dimensions(self) -> str:
        return f'{self.width}x{self.height}'

    @property
    def disk_size(self) -> str:
        index = int(floor(log(self.size, 1024)))
        size = round(self.size / pow(1024, index), 2)

        return f'{size}{DISK_SIZES[index]}'

    @hybrid_property
    def name(self) -> str:
        return f'{self.md5}.{self.ext}'

    @name.inplace.expression
    def name(cls) -> ColumnElement[str]:
        return cls.md5 + '.' + cls.ext

    @property
    def nsfw(self) -> bool:
        """
        Returns True if Post has NSFW tag, or is in a sensitive directory.
        """
        first_part = self.directory.split('/')[0] if self.directory else None
        in_sensitive_dir = first_part in SENSITIVE_DIRS
        nsfw_tag_applied = any(tag.name == NSFW_TAG_NAME for tag in self.tags)

        return in_sensitive_dir or nsfw_tag_applied

    @property
    def path(self) -> Path:
        return CONTENT_PATH / (self.directory or '') / self.name

    @property
    def uri(self) -> str:
        return url_for(
            'Root.Post.view_page',
            post_id = self.id,
            v = self.modified,
            _external = True
        )

    @property
    def view_uri(self) -> str:
        # 2025.10.31 - Added 'v' parameter to trick around caching posts who
        # might have been replaced but the browser hasn't picked it up yet.
        return url_for(
            'Root.Post.view_file_resource',
            post_id = self.id,
            v = self.modified,
            _external = True
        )
