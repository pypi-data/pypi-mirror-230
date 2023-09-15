"""Page view"""

import json
from typing import List, Optional
from kameleoon.data.data import Data, DataType
from kameleoon.network.query_builder import QueryBuilder, QueryParam, QueryParams


class PageView(Data):
    """Page view"""

    EVENT_TYPE = "page"

    def __init__(self, url: str, title: str, referrers: Optional[List[int]] = None) -> None:
        """
        :param url: Url of the page
        :type url: str
        :param title: Title of the page
        :type title: str
        :param referrers: Optional field - Referrer ids
        :type referrers: Optional[List[int]]

        Example:

        .. code-block:: python3

                kameleoon_client.add_data(visitor_code, PageView("www.test.com", "test-title"))
        """
        super().__init__()
        self.url = url
        self.title = title
        self.referrers = referrers
        self._instance: DataType = DataType.PAGE_VIEW

    def obtain_full_post_text_line(self) -> str:
        qb = QueryBuilder(  # pylint: disable=C0103
            QueryParam(QueryParams.EVENT_TYPE, self.EVENT_TYPE),
            QueryParam(QueryParams.HREF, self.url),
            QueryParam(QueryParams.TITLE, self.title),
            QueryParam(QueryParams.NONCE, self._nonce),
        )
        if self.referrers:
            str_referrers = json.dumps(self.referrers, separators=(",", ":"))
            qb.append(QueryParam(QueryParams.REFERRERS_INDICES, str_referrers))
        return str(qb)
