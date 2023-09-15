# pylint: disable=duplicate-code
"""Device data"""

from enum import Enum
from kameleoon.data.data import Data, DataType
from kameleoon.network.query_builder import QueryBuilder, QueryParam, QueryParams


class DeviceType(Enum):
    """Device types"""

    PHONE: str = "PHONE"
    TABLET: str = "TABLET"
    DESKTOP: str = "DESKTOP"


class Device(Data):
    """Device data"""

    EVENT_TYPE = "staticData"

    def __init__(self, device_type: DeviceType) -> None:
        """
        :param device_type: DeviceType, can be: PHONE, TABLET, DESKTOP

        Example:
        .. code-block:: python3
                kameleoon_client.add_data(visitor_code, Device(DeviceType.PHONE))
        """
        super().__init__()
        self.device_type = device_type
        self._instance: DataType = DataType.DEVICE

    def obtain_full_post_text_line(self) -> str:
        return str(
            QueryBuilder(
                QueryParam(QueryParams.EVENT_TYPE, self.EVENT_TYPE),
                QueryParam(QueryParams.DEVICE_TYPE, self.device_type.value),
                QueryParam(QueryParams.NONCE, self._nonce),
            )
        )
