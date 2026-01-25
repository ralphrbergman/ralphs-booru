from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship

class AuthorMixin:
    author_id: Mapped[int] = mapped_column(
        ForeignKey('user.id'),
        nullable = False
    )

    @declared_attr
    def author(cls) -> Mapped['User']:
        return relationship('User', back_populates=f"{cls.__tablename__}s")
