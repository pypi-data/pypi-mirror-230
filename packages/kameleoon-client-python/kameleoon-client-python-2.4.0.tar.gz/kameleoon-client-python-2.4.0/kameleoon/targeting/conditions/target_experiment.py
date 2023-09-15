"""Experiment condition"""
from typing import Any, Union, Dict


from kameleoon.exceptions import NotFoundError
from kameleoon.targeting.conditions.targeting_condition import TargetingCondition
from kameleoon.targeting.conditions.constants import TargetingOperator


class TargetExperiment(TargetingCondition):
    """TargetExperiment represents Experiment condition from back-office"""

    def __init__(self, json_condition: Dict[str, Union[str, int, Any]]):
        super().__init__(json_condition)
        experiment_id_name = "experiment"
        self.experiment_id = int(json_condition.get(experiment_id_name, TargetingCondition.NON_EXISTENT_IDENTIFIER))
        if self.experiment_id == TargetingCondition.NON_EXISTENT_IDENTIFIER:
            raise NotFoundError(experiment_id_name)
        try:
            self.__variation = json_condition.get("variation")
            self.__operator = TargetingOperator[str(json_condition["variationMatchType"])]
        except KeyError as ex:
            self._logger.error("%s has wrong JSON structure: %s", self.__class__, ex)

    def check(self, data) -> bool:
        is_targeted = False
        variation_storage = dict[int, int](data)
        is_saved_variation_storage_exist = bool(variation_storage)
        if self.__operator == TargetingOperator.EXACT:
            saved_variation_value = variation_storage.get(self.experiment_id, 0)
            is_targeted = is_saved_variation_storage_exist and saved_variation_value == self.__variation
        elif self.__operator == TargetingOperator.ANY:
            is_targeted = is_saved_variation_storage_exist
        return is_targeted
