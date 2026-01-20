from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column, validates

from db import db
from .mixins.created import CreatedMixin
from .mixins.id import IdMixin
from .mixins.serializer import SerializerMixin

class Tag(db.Model, CreatedMixin, IdMixin, SerializerMixin):
    id: Mapped[int] = mapped_column(primary_key = True)
    name: Mapped[str] = mapped_column(nullable = False, unique = True)
    
    type: Mapped[str] = mapped_column(server_default = 'general', nullable = False)
    desc: Mapped[str] = mapped_column(nullable = True)

    posts: Mapped[list['Post']] = db.relationship(back_populates = 'tags', secondary = 'tag_association')

    @validates('name', 'desc')
    def validate_tag(self, key: str, value: str) -> Optional[str]:
        value = value.strip()

        if not value:
            return None

        return value
