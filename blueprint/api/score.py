from apiflask import APIBlueprint, abort
from flask_login import current_user

from api import add_vote, delete_score, get_score, remove_vote
from api.decorators import owner_only, post_protect
from db import ScoreAssociation
from db.schemas import ScoreIn, ScoreOut

score_bp = APIBlueprint(
    name = 'Score API',
    import_name = __name__,
    url_prefix = '/score'
)

@score_bp.get('/<int:score_id>')
@score_bp.output(ScoreOut)
def obtain_score(score_id: int):
    score = get_score(score_id)

    if not score:
        abort(404, message = 'Score not found.')

    return score

@score_bp.delete('/<int:score_id>')
@score_bp.output({}, status_code = 204)
@owner_only(ScoreAssociation)
def remove_score(score_id: int, score: ScoreAssociation):
    if not score:
        abort(404, message = 'Score not found')

    delete_score(score)

    return {}

@score_bp.post('')
@score_bp.input(ScoreIn, arg_name = 'data')
@score_bp.output(ScoreOut)
@post_protect
def upload_score(data: ScoreIn):
    value: int = data['value']

    payload = (data['target_id'], current_user.id, data['target_type'])
    score = add_vote(*payload) if value == 1 else remove_vote(*payload)

    return score
