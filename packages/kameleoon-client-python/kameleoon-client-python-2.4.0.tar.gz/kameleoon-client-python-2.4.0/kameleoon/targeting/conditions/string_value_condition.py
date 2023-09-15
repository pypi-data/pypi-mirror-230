"""Device condition"""
import re
from typing import Any, Dict, Optional, Union
from kameleoon.targeting.conditions.constants import TargetingOperator

from kameleoon.targeting.conditions.targeting_condition import TargetingCondition


class StringValueCondition(TargetingCondition):
    """
    String value condition should be used when you need to compare string values

    It should be used as parent class for other conditions
    """

    def __init__(self, json_condition: Dict[str, Union[str, int, Any]], value: Optional[str]):
        super().__init__(json_condition)
        self.__condition_value = value
        try:
            self.__operator = TargetingOperator[str(json_condition["matchType"])]
        except KeyError as ex:
            self._logger.error("Unknown operation for %s condition, error: %s", self.type, ex)

    def check(self, data) -> bool:
        if not isinstance(data, str):
            return False

        return self._check(data)

    def _check(self, value: str):
        if self.__condition_value is None:
            return False

        if self.__operator == TargetingOperator.EXACT:
            return value == self.__condition_value

        if self.__operator == TargetingOperator.CONTAINS:
            return self.__condition_value in value

        if self.__operator == TargetingOperator.REGULAR_EXPRESSION:
            pattern = re.compile(self.__condition_value)
            return bool(re.fullmatch(pattern, value))

        self._logger.error("Unexpected comparing operation for condition: %s", self.__operator)
        return False
