"""CustomData condition"""
import re
import json
from typing import Any, Union, Dict, Optional

from kameleoon.data import CustomData, DataType
from kameleoon.targeting.conditions.targeting_condition import TargetingCondition
from kameleoon.targeting.conditions.constants import TargetingOperator

__all__ = [
    "CustomDatum",
]


class CustomDatum(TargetingCondition):
    """CustomDatum represents a Custom Data condition from back-office"""

    def __init__(self, json_condition: Dict[str, Union[str, Any]]):
        super().__init__(json_condition)
        try:
            self.__index = json_condition["customDataIndex"]
            self.__operator = TargetingOperator[json_condition["valueMatchType"]]
        except KeyError as ex:
            self._logger.error("%s has wrong JSON structure: %s", self.__class__, ex)
        self.value = json_condition.get("value", None)

    # pylint: disable=R0912,R0915
    def check(self, data) -> bool:  # noqa: C901
        is_targeted = False
        custom_data = self.__get_last_custom_data(data)
        if not custom_data:
            is_targeted = self.__operator == TargetingOperator.UNDEFINED
        else:
            if self.__operator == TargetingOperator.REGULAR_EXPRESSION:
                try:
                    pattern = re.compile(self.value)
                    is_targeted = any(re.fullmatch(pattern, val) is not None for val in custom_data.values)
                except re.error as err:
                    self._logger.error(err)
            elif self.__operator == TargetingOperator.CONTAINS:
                is_targeted = any(self.value in val for val in custom_data.values)
            elif self.__operator == TargetingOperator.EXACT:
                is_targeted = self.value in custom_data.values
            elif self.__operator == TargetingOperator.EQUAL:
                try:
                    value = float(self.value)
                    is_targeted = any(float(val) == value for val in custom_data.values)
                except ValueError as err:
                    self._logger.error(err)
            elif self.__operator == TargetingOperator.GREATER:
                try:
                    value = float(self.value)
                    is_targeted = any(float(val) > value for val in custom_data.values)
                except ValueError as err:
                    self._logger.error(err)
            elif self.__operator == TargetingOperator.LOWER:
                try:
                    value = float(self.value)
                    is_targeted = any(float(val) < value for val in custom_data.values)
                except ValueError as err:
                    self._logger.error(err)
            elif self.__operator == TargetingOperator.TRUE:
                is_targeted = "true" in custom_data.values
            elif self.__operator == TargetingOperator.FALSE:
                is_targeted = "false" in custom_data.values
            elif self.__operator == TargetingOperator.AMONG_VALUES:
                try:
                    # Possible issues with float values.
                    all_matches = json.loads(self.value)
                    parse_dict = {False: "false", True: "true"}
                    condtition_values = {parse_dict.get(m, str(m)) for m in all_matches}
                    is_targeted = any(val in condtition_values for val in custom_data.values)
                except json.JSONDecodeError as err:
                    self._logger.error(err)
            elif self.__operator != TargetingOperator.UNDEFINED:
                self._logger.error("UNDEFINED operator found in unexpected case")
        return is_targeted

    def __get_last_custom_data(self, data) -> Optional[CustomData]:
        data_type = DataType.CUSTOM_DATA
        # pylint: disable=W0212
        data_iter = iter(x for x in reversed(data) if (x._instance == data_type) and (x.id == self.__index))
        return next(data_iter, None)
