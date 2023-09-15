"""Unknown condition"""
from kameleoon.targeting.conditions.targeting_condition import TargetingCondition


class UnknownCondition(TargetingCondition):
    """
    Unknown condition creates when data file contains unknown targeting type,

    This condition always returns targeting result (True)
    """

    def check(self, data) -> bool:
        return True
