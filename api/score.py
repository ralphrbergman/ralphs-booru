from sqlalchemy import and_, select
from db import Score, db

def _set_vote(post_id: int, user_id: int, value: int) -> Score:
    score = get_vote(
        post_id = post_id,
        user_id = user_id
    )

    if not score:
        score = Score(post_id = post_id, user_id = user_id)
        db.session.add(score)

    score.value = value

    db.session.commit()
    return score

def add_vote(post_id: int, user_id: int) -> Score:
    return _set_vote(post_id = post_id, user_id = user_id, value = 1)

def get_vote(post_id: int, user_id: int) -> Score:
    score = db.session.scalars(
        select(Score)\
        .where(
            and_(
                Score.post_id == post_id,
                Score.user_id == user_id
            )
        )
    ).first()

    return score

def remove_vote(post_id: int, user_id: int) -> Score:
    return _set_vote(post_id = post_id, user_id = user_id, value = -1)
