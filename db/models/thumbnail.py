from flask import url_for
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import db
from .mixins.created import CreatedMixin
from .mixins.id import IdMixin
from .mixins.serializer import SerializerMixin

class Thumbnail(db.Model, CreatedMixin, IdMixin, SerializerMixin):
    id: Mapped[int] = mapped_column(primary_key = True)
    post_id: Mapped[int] = mapped_column(ForeignKey('post.id'), nullable = False, unique = True)
    post: Mapped['Post'] = relationship('Post', back_populates = 'thumbnail')
    data: Mapped[bytes] = mapped_column(nullable = False)

    @property
    def view_uri(self) -> str:
        return url_for('Root.Thumbnail.thumbnail_route', post_id = self.post_id, _external = True)
