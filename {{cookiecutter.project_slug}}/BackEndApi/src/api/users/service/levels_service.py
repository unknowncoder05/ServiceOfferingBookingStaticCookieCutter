from __future__ import annotations

from django.db.models import QuerySet

from api.cms.models import ContentLittleRobinLevels


class LevelsSearch:
    _level = None
    total_investment: float

    def __init__(self, total_investment: float):
        self.total_investment = total_investment

    def is_level_available(self, total_investment: float) -> bool:
        all_levels = ContentLittleRobinLevels.objects.order_by('target_amount').first()
        if not total_investment:
            return False
        if total_investment >= all_levels.target_amount.amount:
            return True
        return False

    @property
    def get_level(self) -> ContentLittleRobinLevels | None:
        levels: QuerySet[ContentLittleRobinLevels] = ContentLittleRobinLevels.objects.all().order_by('-target_amount')
        for level in levels:
            if level.target_amount.amount <= self.total_investment:
                return level
        return None

    @property
    def get_next_level(self) -> ContentLittleRobinLevels | None:
        levels: QuerySet[ContentLittleRobinLevels] = ContentLittleRobinLevels.objects.all().order_by('target_amount')
        for level in levels:
            if level.target_amount.amount > self.total_investment:
                return level
        return None
