from typing import Optional

from sqlalchemy import and_, select
from sqlalchemy.exc import IntegrityError

from db import ScoreAssociation, db

def _set_vote(
    target_id: int,
    user_id: int,
    score_type: str,
    value: int
) -> Optional[ScoreAssociation]:
    """
    Changes score of a vote.
    Creates vote if it doesn't exist.

    Args:
        target_id: Target's ID, this is equivalent to post's ID
        user_id: Voter's ID
        score_type: Target type (e.g post)
        value: -1 for negative votes and 1 for positive
    """
    score = get_vote(
        target_id = target_id,
        user_id = user_id,
        score_type = score_type
    )

    if not score:
        score = ScoreAssociation(
            target_id = target_id,
            user_id = user_id,
            target_type = score_type
        )
        db.session.add(score)

    score.value = value

    try:
        db.session.commit()
    except IntegrityError as exception:
        print(exception)
        db.session.rollback()
        return

    return score

def add_vote(
    target_id: int,
    user_id: int,
    score_type: str
) -> ScoreAssociation:
    """
    Positively adds vote.

    Args:
        target_id: Post ID (example)
        user_id: Voter's ID
        score_type: (e.g post)
    """
    return _set_vote(
        target_id = target_id,
        user_id = user_id,
        score_type = score_type,
        value = 1
    )

def delete_score(score: ScoreAssociation) -> None:
    """
    Deletes score.
    """
    db.session.delete(score)

def get_vote(
    target_id: int,
    user_id: int,
    score_type: str = None
) -> Optional[ScoreAssociation]:
    """
    Obtains vote.

    Args:
        target_id: post ID (example)
        user_id: Voter's ID
        score_type: (e.g post)
    """
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
    """
    Obtains score from its ID.
    """
    return db.session.scalars(
        select(ScoreAssociation)
        .where(ScoreAssociation.id == score_id)
    ).first()

def remove_vote(
    target_id: int,
    user_id: int,
    score_type: str
) -> ScoreAssociation:
    """
    Negatively adds vote.

    Args:
        target_id: comment ID (example)
        user_id: Voter's ID
        score_type: (e.g comment)
    """
    return _set_vote(
        target_id = target_id,
        user_id = user_id,
        score_type = score_type,
        value = -1
    )
