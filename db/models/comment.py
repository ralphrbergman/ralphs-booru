from datetime import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import db
from .mixins.score import ScoreMixin

class Comment(db.Model, ScoreMixin):
    id: Mapped[int] = mapped_column(primary_key = True)
    created: Mapped[datetime] = mapped_column(default = func.now())

    author_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable = False)
    author: Mapped['User'] = relationship(back_populates = 'comments')

    post_id: Mapped[int] = mapped_column(ForeignKey('post.id'), nullable = False)
    post: Mapped['Post'] = relationship(back_populates = 'comments')

    content: Mapped[str] = mapped_column(nullable = False)

    scores: Mapped[list['ScoreAssociation']] = relationship(
        'ScoreAssociation',
        primaryjoin="and_(Comment.id == foreign(ScoreAssociation.target_id), ScoreAssociation.target_type == 'comment')",
        viewonly=True,
        overlaps="scores"
    )
