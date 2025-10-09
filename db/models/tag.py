from datetime import datetime
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, validates

from db import db

class Tag(db.Model):
    id: Mapped[int] = mapped_column(primary_key = True)
    name: Mapped[str] = mapped_column(nullable = False, unique = True)
    created: Mapped[datetime] = mapped_column(default = func.now())

    @validates('name')
    def validate_name(self, key: str, value: str) -> Optional[str]:
        if not value.strip():
            return None

        return value
