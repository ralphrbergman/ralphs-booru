from sqlalchemy import func, and_, select
from sqlalchemy.sql import ColumnElement
from sqlalchemy.ext.hybrid import hybrid_property

from ..score_assoc import ScoreAssociation

class ScoreMixin:
    @hybrid_property
    def score(self) -> int:
        return sum(score.value for score in self.scores)

    @score.inplace.expression
    def score(cls) -> ColumnElement[int]:
        subquery = (
            select(func.coalesce(func.sum(ScoreAssociation.value), 0))
            .where(
                and_(
                    ScoreAssociation.target_id == cls.id,
                    ScoreAssociation.target_type == 'post'
                )
            )
            .correlate(cls) # This tells SQL exactly which "id" to use
        ).scalar_subquery()
        
        return subquery
