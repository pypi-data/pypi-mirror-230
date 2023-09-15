"""Browser data"""

from enum import IntEnum
from typing import Optional
from kameleoon.data.data import Data, DataType
from kameleoon.exceptions import KameleoonException
from kameleoon.network.query_builder import QueryBuilder, QueryParam, QueryParams


class BrowserType(IntEnum):
    """Browser types"""

    CHROME: int = 0
    INTERNET_EXPLORER: int = 1
    FIREFOX: int = 2
    SAFARI: int = 3
    OPERA: int = 4
    OTHER: int = 5


class Browser(Data):
    """Browser data"""

    EVENT_TYPE = "staticData"

    def __init__(self, browser_type: BrowserType, version: Optional[float] = None) -> None:
        """
        :param browser_type: BrowserType, can be: CHROME, INTERNET_EXPLORER, FIREFOX, SAFARI, OPERA, OTHER

        Example:

        .. code-block:: python3

                kameleoon_client.add_data(visitor_code, Browser(BrowserType.CHROME))
        """
        super().__init__()
        self.browser_type = browser_type
        self.version = version
        self._instance: DataType = DataType.BROWSER

    def obtain_full_post_text_line(self) -> str:
        if self.browser_type < 0:
            raise KameleoonException("Browser not recognized")
        query_builder = QueryBuilder(
            QueryParam(QueryParams.EVENT_TYPE, self.EVENT_TYPE),
            QueryParam(QueryParams.BROWSER_INDEX, str(self.browser_type.value)),
            QueryParam(QueryParams.NONCE, self._nonce),
        )
        if self.version:
            query_builder.append(QueryParam(QueryParams.BROWSER_VERSION, str(self.version)))
        return str(query_builder)
