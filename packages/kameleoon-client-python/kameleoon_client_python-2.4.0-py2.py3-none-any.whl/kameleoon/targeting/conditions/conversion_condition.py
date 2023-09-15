"""Conversion condition"""
from typing import Any, Dict, Optional, Union
from kameleoon.data import Conversion, DataType

from kameleoon.targeting.conditions.targeting_condition import TargetingCondition


class ConversionCondition(TargetingCondition):
    """Conversion condition uses in case if you need to target users by their conversion"""

    def __init__(self, json_condition: Dict[str, Union[str, int, Any]]):
        super().__init__(json_condition)
        try:
            self.__goal_id = json_condition.get("goalId", TargetingCondition.NON_EXISTENT_IDENTIFIER)
        except KeyError as ex:
            self._logger.error("%s has wrong JSON structure: %s", self.__class__, ex)

    def check(self, data) -> bool:
        conversion: Optional[Conversion] = self.get_last_targeting_data(data, DataType.CONVERSION)
        return conversion is not None and self.__goal_id in (
            TargetingCondition.NON_EXISTENT_IDENTIFIER,
            conversion.goal_id,
        )
