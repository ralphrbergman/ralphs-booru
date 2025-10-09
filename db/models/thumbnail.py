from base64 import b64encode

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import db

class Thumbnail(db.Model):
    id: Mapped[int] = mapped_column(primary_key = True)
    post_id: Mapped[int] = mapped_column(ForeignKey('post.id'), nullable = False, unique = True)
    post: Mapped['Post'] = relationship('Post', back_populates = 'thumbnail')
    data: Mapped[bytes] = mapped_column(nullable = False)

    @property
    def enc_data(self) -> str:
        return b64encode(self.data).decode()
