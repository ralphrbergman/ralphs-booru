from datetime import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import db

class Comment(db.Model):
    id: Mapped[int] = mapped_column(primary_key = True)
    created: Mapped[datetime] = mapped_column(default = func.now())

    author_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable = False)
    author: Mapped['User'] = relationship(back_populates = 'comments')

    post_id: Mapped[int] = mapped_column(ForeignKey('post.id'), nullable = False)
    post: Mapped['Post'] = relationship(back_populates = 'comments')

    content: Mapped[str] = mapped_column(nullable = False)
