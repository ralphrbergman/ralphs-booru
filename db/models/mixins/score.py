class ScoreMixin:
    @property
    def total_score(self) -> int:
        return sum(score.value for score in self.scores)
