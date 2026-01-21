from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from db import db
from .mixins.id import IdMixin

class Permission(db.Model, IdMixin):
    slug: Mapped[str] = mapped_column(String(25), nullable = False, unique = True)
