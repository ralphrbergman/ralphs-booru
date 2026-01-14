from apiflask import APIBlueprint
from flask_login import current_user, login_required

from api import add_vote, get_vote, remove_vote
from db.schemas import ScoreIn, ScoreOut

score_bp = APIBlueprint(
    name = 'Score API',
    import_name = __name__,
    url_prefix = '/score'
)

@score_bp.delete('')
@login_required
@score_bp.input(ScoreIn, arg_name = 'data', location = 'query')
@score_bp.output(ScoreOut)
def downvote_route(data: ScoreIn):
    score = remove_vote(post_id = data['post_id'], user_id = current_user.id)

    return score

@score_bp.post('')
@login_required
@score_bp.input(ScoreIn, arg_name = 'data', location = 'query')
@score_bp.output(ScoreOut)
def upvote_route(data: ScoreIn):
    score = add_vote(post_id = data['post_id'], user_id = current_user.id)

    return score
