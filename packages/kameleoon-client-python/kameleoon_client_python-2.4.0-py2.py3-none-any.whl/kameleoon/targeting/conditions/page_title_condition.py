""" condition"""
from typing import Any, Optional, Union, Dict
from kameleoon.data import DataType, PageView

from kameleoon.targeting.conditions.string_value_condition import StringValueCondition


class PageTitleCondition(StringValueCondition):
    """Page title condition uses when you need to compare title of page"""

    def __init__(self, json_condition: Dict[str, Union[str, Any]]):
        super().__init__(json_condition, json_condition.get("title"))

    def check(self, data) -> bool:
        page_view: Optional[PageView] = self.get_last_targeting_data(data, DataType.PAGE_VIEW)
        return page_view is not None and self._check(page_view.title)
