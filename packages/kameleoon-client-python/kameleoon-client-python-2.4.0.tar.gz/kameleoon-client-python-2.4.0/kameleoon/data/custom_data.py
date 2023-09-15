"""Custom data"""

import json
from typing import Optional, Tuple
import warnings
from kameleoon.data.data import Data, DataType
from kameleoon.network.query_builder import QueryBuilder, QueryParam, QueryParams


class CustomData(Data):
    """Custom data"""

    EVENT_TYPE = "customData"

    @property
    def values(self) -> Tuple[str, ...]:
        """Stored values."""
        return self.__values

    def __init__(self, id: int, *args: str, value: Optional[str] = None) -> None:
        """
        :param id: Index / ID of the custom data to be stored. This field is mandatory.
        :type id: int
        :param `*args`: Values of the custom data to be stored. This field is optional.
        :type `*args`: Tuple[str, ...]
        :param value: Single value of the custom data to be stored. This field is optional.
        :type value: Optional[str]

        Example:

        .. code-block:: python3

                kameleoon_client.add_data(visitor_code, CustomData(123, "some-value"))
        """
        # pylint: disable=invalid-name,redefined-builtin
        super().__init__()
        self.id = str(id)
        if value is None:
            self.__values = args
        else:
            self.__values = (*args, value)
            warnings.warn(
                "Passing deprecated parameter `value`. Please pass variadic parameter list instead.",
                category=DeprecationWarning,
            )
        self._instance: DataType = DataType.CUSTOM_DATA

    def obtain_full_post_text_line(self) -> str:
        if len(self.__values) == 0:
            return ""
        str_values = json.dumps({v: 1 for v in self.__values}, separators=(",", ":"))
        return str(
            QueryBuilder(
                QueryParam(QueryParams.EVENT_TYPE, self.EVENT_TYPE),
                QueryParam(QueryParams.INDEX, self.id),
                QueryParam(QueryParams.VALUES_COUNT_MAP, str_values),
                QueryParam(QueryParams.OVERWRITE, "true"),
                QueryParam(QueryParams.NONCE, self._nonce),
            )
        )
