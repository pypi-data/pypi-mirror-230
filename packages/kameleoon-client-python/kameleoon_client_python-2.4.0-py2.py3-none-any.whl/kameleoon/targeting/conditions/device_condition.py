"""Device condition"""
from typing import Any, Dict, Optional, Union
from kameleoon.data import Device
from kameleoon.data.data import DataType
from kameleoon.data.device import DeviceType

from kameleoon.targeting.conditions.targeting_condition import TargetingCondition


class DeviceCondition(TargetingCondition):
    """Device condition uses in case if you need to target by device type"""

    def __init__(self, json_condition: Dict[str, Union[str, int, Any]]):
        super().__init__(json_condition)
        try:
            self.__device_type = DeviceType[str(json_condition.get("device", "")).upper()]
        except KeyError as ex:
            self._logger.error("%s has wrong JSON structure: %s", self.__class__, ex)

    def check(self, data) -> bool:
        device: Optional[Device] = self.get_last_targeting_data(data, DataType.DEVICE)
        return device is not None and self.__device_type is not None and device.device_type == self.__device_type
