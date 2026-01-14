from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import db

class Score(db.Model):
    __tablename__ = 'score_association'

    post_id: Mapped[int] = mapped_column(ForeignKey('post.id'), primary_key = True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), primary_key = True)
    value: Mapped[int] = mapped_column(nullable = False)

    post: Mapped['Post'] = relationship('Post', back_populates = 'scores')
    user: Mapped['User'] = relationship('User', back_populates = 'scores')
