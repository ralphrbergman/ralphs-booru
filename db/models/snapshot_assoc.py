from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from db import db

class TagSnapshotAssociation(db.Model):
    __tablename__ = 'tag_snapshot_association'

    snapshot_id: Mapped[int] = mapped_column(
        ForeignKey('snapshot.id'),
        primary_key = True
    )
    tag_id: Mapped[int] = mapped_column(
        ForeignKey('tag.id'),
        primary_key = True
    )

    __table_args__ = (
        UniqueConstraint('snapshot_id', 'tag_id', name = 'uq_snapshot_tag'),
    )
