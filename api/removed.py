from typing import Any

from db import RemovedLog, User, db

def create_log(entity: Any, moderator: User, reason: str) -> RemovedLog:
    """
    Creates new removed log.

    Args:
        entity: Entity to flag as removed
        moderator: Someone who performs the action
        reason: Reason
    """
    log = RemovedLog()

    log.entity_id = getattr(entity, 'id')
    log.entity_type = entity.__class__.__name__
    log.by_id = moderator.id
    log.reason = reason[:150]

    setattr(entity, 'removed', True)
    setattr(entity, 'log_id', log.id)

    db.session.add(log)
    return log

def delete_log(entity: Any) -> None:
    """
    Marks removed log deleted.
    """
    log = getattr(entity, 'log')
    setattr(entity, 'removed', False)

    if not log:
        return

    db.session.delete(log)
