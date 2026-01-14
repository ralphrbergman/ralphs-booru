from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from db import db

class TagAssociation(db.Model):
    __tablename__ = 'tag_association'

    post_id: Mapped[int] = mapped_column(ForeignKey('post.id'), primary_key = True)
    tag_id: Mapped[int] = mapped_column(ForeignKey('tag.id'), primary_key = True)

    __table_args__ = (
        UniqueConstraint('post_id', 'tag_id', name = 'uq_post_tag'),
    )
