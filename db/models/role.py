from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import db
from .mixins.id import IdMixin

class Role(db.Model, IdMixin):
    name: Mapped[str] = mapped_column(String(25), nullable = False, unique = True)

    # Relationships.
    permissions: Mapped[list['Permission']] = relationship(
        secondary = 'role_perms'
    )
