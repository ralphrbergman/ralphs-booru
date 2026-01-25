from typing import Optional

from sqlalchemy import and_, text
from sqlalchemy.orm import (
    Mapped,
    declared_attr,
    foreign,
    mapped_column,
    relationship
)

from ..removed import RemovedLog

class RemovedMixin:
    removed: Mapped[bool] = mapped_column(
        default = False,
        nullable = False,
        server_default = text('0')
    )

    @declared_attr
    def log(cls) -> Mapped[Optional[RemovedLog]]:
        return relationship(
            primaryjoin = lambda: and_(
                cls.id == foreign(RemovedLog.entity_id),
                RemovedLog.entity_type == cls.__name__
            ),
            uselist = False,
            viewonly = True
        )
