from datetime import datetime
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, validates

from db import db
from .tag_assoc import TagAssociation

class Tag(db.Model):
    id: Mapped[int] = mapped_column(primary_key = True)
    name: Mapped[str] = mapped_column(nullable = False, unique = True)
    created: Mapped[datetime] = mapped_column(default = func.now())
    type: Mapped[str] = mapped_column(server_default = 'general', nullable = False)
    desc: Mapped[str] = mapped_column(nullable = True)
    posts: Mapped[list['Post']] = db.relationship('Post', secondary = TagAssociation, back_populates = 'tags')

    @validates('name', 'desc')
    def validate_tag(self, key: str, value: str) -> Optional[str]:
        value = value.strip()

        if not value:
            return None

        return value
