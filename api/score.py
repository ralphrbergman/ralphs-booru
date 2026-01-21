from typing import Optional

from sqlalchemy import and_, select
from sqlalchemy.exc import IntegrityError

from db import ScoreAssociation, db

def _set_vote(target_id: int, user_id: int, score_type: str, value: int) -> Optional[ScoreAssociation]:
    score = get_vote(
        target_id = target_id,
        user_id = user_id,
        score_type = score_type
    )

    if not score:
        score = ScoreAssociation(target_id = target_id, user_id = user_id, target_type = score_type)
        db.session.add(score)

    score.value = value

    try:
        db.session.commit()
    except IntegrityError as exc:
        print(exc)
        db.session.rollback()
        return

    return score

def add_vote(target_id: int, user_id: int, score_type: str) -> ScoreAssociation:
    return _set_vote(
        target_id = target_id,
        user_id = user_id,
        score_type = score_type,
        value = 1
    )

def delete_score(score: ScoreAssociation) -> None:
    db.session.delete(score)

def get_vote(target_id: int, user_id: int, score_type: str = None) -> Optional[ScoreAssociation]:
    score = db.session.scalars(
        select(ScoreAssociation)\
        .where(
            and_(
                ScoreAssociation.target_id == target_id,
                ScoreAssociation.user_id == user_id,
                ScoreAssociation.target_type == score_type
            )
        )
    ).first()

    return score

def get_score(score_id: int) -> Optional[ScoreAssociation]:
    return db.session.scalars(
        select(ScoreAssociation)
        .where(ScoreAssociation.id == score_id)
    ).first()

def remove_vote(target_id: int, user_id: int, score_type: str) -> ScoreAssociation:
    return _set_vote(
        target_id = target_id,
        user_id = user_id,
        score_type = score_type,
        value = -1
    )
