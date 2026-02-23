from sqlalchemy import ForeignKey, and_, desc
from sqlalchemy.orm import (
    Mapped,
    foreign,
    mapped_column,
    remote,
    relationship
)

from db import db
from .mixins.created import CreatedMixin
from .mixins.id import IdMixin
from .mixins.sortable import SortableMixin
from .user import User

class Snapshot(db.Model, CreatedMixin, IdMixin, SortableMixin):
    post_id: Mapped[int] = mapped_column(
        ForeignKey(
            'post.id',
            ondelete = 'cascade'
        ), index = True
    )
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            'user.id',
            ondelete = 'set null'
        )
    )
    tags: Mapped[list['Tag']] = relationship(
        'Tag',
        secondary = 'tag_snapshot_association',
        back_populates = 'snapshots'
    )

    # Relationships.
    post: Mapped['Post'] = relationship(back_populates = 'snapshots')
    user: Mapped[User | None] = relationship(back_populates = 'snapshots')

    previous: Mapped['Snapshot'] = relationship(
        order_by=lambda: desc(remote(Snapshot.id)),
        overlaps="snapshots",
        primaryjoin=lambda: and_(
            Snapshot.post_id == remote(Snapshot.post_id),
            Snapshot.id > foreign(remote(Snapshot.id))
        ),
        viewonly=True,
        uselist=False,
    )
