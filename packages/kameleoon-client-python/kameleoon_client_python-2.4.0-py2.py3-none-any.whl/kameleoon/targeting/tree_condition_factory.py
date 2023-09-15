"""Targeting condition factory"""
from kameleoon.targeting.conditions.browser_condition import BrowserCondition
from kameleoon.targeting.conditions.conversion_condition import ConversionCondition
from kameleoon.targeting.conditions.device_condition import DeviceCondition
from kameleoon.targeting.conditions.page_title_condition import PageTitleCondition
from kameleoon.targeting.conditions.page_url_condition import PageUrlCondition
from kameleoon.targeting.conditions.sdk_language_condition import SdkLanguageCondition
from kameleoon.targeting.conditions.unknown_condition import UnknownCondition
from kameleoon.targeting.conditions.targeting_condition import TargetingCondition, TargetingConditionType
from kameleoon.targeting.conditions.custom_datum import CustomDatum
from kameleoon.targeting.conditions.target_experiment import TargetExperiment
from kameleoon.targeting.conditions.exclusive_experiment import ExclusiveExperiment
from kameleoon.targeting.conditions.visitor_code_condition import VisitorCodeCondition


class TreeConditionFactory:
    """Factory of targeting condition types"""

    @staticmethod
    def get_condition(condition_json) -> TargetingCondition:  # noqa: C901 pylint: disable=R0911
        """Create a proper condition from the given json object"""
        try:
            targeting_type = condition_json.get("targetingType", TargetingConditionType.UNKNOWN.value)
            condition_type = TargetingConditionType[targeting_type]
            if condition_type == TargetingConditionType.CUSTOM_DATUM:
                return CustomDatum(condition_json)

            if condition_type == TargetingConditionType.TARGET_EXPERIMENT:
                return TargetExperiment(condition_json)

            if condition_type == TargetingConditionType.EXCLUSIVE_EXPERIMENT:
                return ExclusiveExperiment(condition_json)

            if condition_type == TargetingConditionType.DEVICE_TYPE:
                return DeviceCondition(condition_json)

            if condition_type == TargetingConditionType.VISITOR_CODE:
                return VisitorCodeCondition(condition_json)

            if condition_type == TargetingConditionType.PAGE_URL:
                return PageUrlCondition(condition_json)

            if condition_type == TargetingConditionType.PAGE_TITLE:
                return PageTitleCondition(condition_json)

            if condition_type == TargetingConditionType.SDK_LANGUAGE:
                return SdkLanguageCondition(condition_json)

            if condition_type == TargetingConditionType.CONVERSIONS:
                return ConversionCondition(condition_json)

            if condition_type == TargetingConditionType.BROWSER:
                return BrowserCondition(condition_json)

            return UnknownCondition(condition_json)
        except KeyError as exception:
            print(f"Unsupported targeted condition type found: {exception}")
            return UnknownCondition(condition_json)
