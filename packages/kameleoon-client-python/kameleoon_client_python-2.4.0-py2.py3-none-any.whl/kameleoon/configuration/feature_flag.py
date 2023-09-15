"""Kameleoon Configuration"""

from typing import Any, List, Dict, Optional

from kameleoon.configuration.rule import Rule
from kameleoon.configuration.variation import Variation


class FeatureFlag:
    """
    FeatureFlag is used for operating feature flags with rules
    """

    @staticmethod
    def from_array(array: List[Dict[str, Any]]) -> List["FeatureFlag"]:
        """Create a list of FeatureFlags from the json array"""
        return [FeatureFlag(item) for item in array]

    def __init__(self, dict_json: Dict[str, Any]):
        self.id_: int = dict_json.get("id", 0)
        self.feature_key: str = dict_json.get("featureKey", "")
        self.default_variation_key: str = dict_json.get("defaultVariationKey", "")
        self.variations: List[Variation] = Variation.from_array(
            dict_json.get("variations", [])
        )
        self.rules: List[Rule] = Rule.from_array(dict_json.get("rules", []))

    def get_variation(self, key: str) -> Optional[Variation]:
        """Retrun a variation for the given key"""
        return next((v for v in self.variations if v.key == key), None)
