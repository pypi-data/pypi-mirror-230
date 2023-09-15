""" Kameleoon Variation Storage """

from typing import Dict, Optional
from kameleoon.storage.visitor_variation import VisitorVariation


class VariationStorage:
    """VariationStorage is a storage of variations for already associated visitors"""

    def __init__(self) -> None:
        """
        VariationStorage saves associated visitor variation (contains id of variation)
        with experiment id for visitor code
        """
        self.storage: Dict[str, Dict[int, VisitorVariation]] = {}

    def get_variation_id(self, visitor_code: str, experiment_id: int) -> Optional[int]:
        """
        Getting variation id if it was already associated for visitor code and for experiment
        despite of respool time
        """
        return self.is_variation_id_valid(visitor_code, experiment_id, None)

    def is_variation_id_valid(
        self, visitor_code: str, experiment_id: int, respool_time: Optional[int] = None
    ) -> Optional[int]:
        """
        Checking if variation id is already associated and valid for visitor code and for experiment.
        Respool time is matter. It checks that variation wasn't already respooled
        """
        if (
            self.storage.get(visitor_code) is not None
            and self.storage[visitor_code].get(experiment_id) is not None
        ):
            variation = self.storage[visitor_code][experiment_id]
            return variation.id_ if variation.is_valid(respool_time) else None
        return None

    def update_variation(
        self, visitor_code: str, experiment_id: int, variation_id: int
    ):
        """
        Updates or adds variation id for visitor code and for experiment
        """
        if self.storage.get(visitor_code) is None:
            self.storage[visitor_code] = {}
        storage_visitor_code = self.storage.get(visitor_code)
        if storage_visitor_code is not None:
            storage_visitor_code[experiment_id] = VisitorVariation(variation_id)

    def get_saved_variation_id(self, visitor_code: str) -> Dict[int, int]:
        """
        Getting dictionary of all associated variation ids for experiments for specific visitor code
        """
        dict_saved_varation_id = {}
        storage_visitor_code = self.storage.get(visitor_code)
        if storage_visitor_code:
            dict_saved_varation_id = {
                key: value.id_ for key, value in storage_visitor_code.items()
            }
        return dict_saved_varation_id
