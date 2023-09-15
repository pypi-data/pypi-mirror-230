"""Exclusive Campaign condition"""
from typing import Any, Union, Dict

from kameleoon.targeting.conditions.targeting_condition import TargetingCondition


class ExclusiveExperiment(TargetingCondition):
    """ExclusiveExperiment represents Exclusive Campaign condition from back-office"""

    def __init__(self, json_condition: Dict[str, Union[str, int, Any]]):
        super().__init__(json_condition)

    def check(self, data) -> bool:
        """Need to return true if variation storage is empty or
        it has only single current experiment in the storage
        """
        current_experiment_id = data[0]
        variation_storage = data[1]
        # check if variation storage is empty
        is_variation_storage_empty = not variation_storage
        # check variation storage has only single experiment and it's current exclusive experiment
        is_current_experiment_single = (
            not is_variation_storage_empty
            and len(variation_storage) == 1
            and variation_storage.get(current_experiment_id) is not None
        )
        return is_variation_storage_empty or is_current_experiment_single
