from typing import Any

from db import RemovedLog, User, db

def create_log(entity: Any, moderator: User, reason: str) -> RemovedLog:
    log = RemovedLog()

    log.entity_id = entity.id
    log.entity_type = entity.__class__.__name__
    log.by_id = moderator.id
    log.reason = reason[:150]

    entity.removed = True
    entity.log_id = log.id

    db.session.add(log)
    return log
