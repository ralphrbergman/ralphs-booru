from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import db
from .mixins.author import AuthorMixin
from .mixins.created import CreatedMixin
from .mixins.id import IdMixin
from .mixins.score import ScoreMixin

class Comment(db.Model, AuthorMixin, CreatedMixin, IdMixin, ScoreMixin):
    post_id: Mapped[int] = mapped_column(ForeignKey('post.id'), nullable = False)
    post: Mapped['Post'] = relationship(back_populates = 'comments')

    content: Mapped[str] = mapped_column(nullable = False)

    scores: Mapped[list['ScoreAssociation']] = relationship(
        'ScoreAssociation',
        primaryjoin="and_(Comment.id == foreign(ScoreAssociation.target_id), ScoreAssociation.target_type == 'comment')",
        viewonly=True,
        overlaps="scores"
    )
