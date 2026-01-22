from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from db import db

class RolePerms(db.Model):
    __tablename__ = 'role_perms'

    permission_id: Mapped[int] = mapped_column(
        ForeignKey('permission.id',
            ondelete = 'cascade'
        ),
        primary_key = True
    )
    role_id: Mapped[int] = mapped_column(
        ForeignKey('role.id',
            ondelete = 'cascade'
        ),
        primary_key = True
    )
