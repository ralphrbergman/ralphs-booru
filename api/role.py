from typing import Optional

from sqlalchemy import select

from db import Role, db

def get_role_by_priority(priority: int) -> Optional[Role]:
    """
    Returns role by its priority.
    """
    """
    Gets role from its priority.

    Args:
        priority: Role's priority
    """
    return db.session.scalar(
        select(Role).where(Role.priority == priority)
    )
