from datetime import datetime
from typing import Any, Optional

from sqlalchemy import ForeignKey, ForeignKeyConstraint, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import db
from .mixins.id import IdMixin

class RemovedLog(db.Model, IdMixin):
    entity_id: Mapped[int] = mapped_column(nullable = False)
    entity_type: Mapped[str] = mapped_column(
        String(length = 15),
        nullable = False
    )

    by_id: Mapped[int] = mapped_column(
        ForeignKey('user.id'),
        nullable = False
    )
    by: Mapped['User'] = relationship(back_populates = 'removed')
    date: Mapped[datetime] = mapped_column(
        default = func.now(),
        nullable = False
    )
    reason: Mapped[str] = mapped_column(
        String(length = 150),
        nullable = False
    )

    @property
    def entity(self) -> Optional[Any]:
        cls = db.Model.registry._class_registry.get(self.entity_type)
        return db.session.get(cls, self.entity_id) if cls else None

    __table_args__ = (
        ForeignKeyConstraint(
            ['by_id'],
            ['user.id'],
            name='fk_removed_log_user'
        ),
    )
