from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import db
from .mixins.id import IdMixin

class ScoreAssociation(db.Model, IdMixin):
    __tablename__ = 'score_association'

    target_id: Mapped[int] = mapped_column()
    target_type: Mapped[str] = mapped_column(String(length = 10), nullable = False)

    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    value: Mapped[int] = mapped_column(nullable = False)

    post: Mapped['Post'] = relationship(
        'Post', 
        primaryjoin="and_(ScoreAssociation.target_id==Post.id, ScoreAssociation.target_type=='post')",
        foreign_keys=[target_id],
        viewonly=True
    )

    user: Mapped['User'] = relationship('User', back_populates = 'scores')

    __table_args__ = (
        UniqueConstraint('target_id', 'target_type', 'user_id', name='user_target_type_uc'),
    )
