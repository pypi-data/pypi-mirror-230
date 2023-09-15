# pylint: disable=duplicate-code
"""Conversion data"""
from kameleoon.data.data import Data, DataType
from kameleoon.network.query_builder import QueryBuilder, QueryParam, QueryParams


# pylint: disable=R0801
class Conversion(Data):
    """Conversion is used for tracking visitors conversions"""

    EVENT_TYPE = "conversion"

    def __init__(self, goal_id: int, revenue: float = 0.0, negative: bool = False) -> None:
        """
        :param goal_id: Id of the goal associated to the conversion
        :type goal_id: int
        :param revenue: Optional field - Revenue associated to the conversion, defaults to 0.0
        :type revenue: float
        :param negative: Optional field - If the revenue is negative. By default it's positive, defaults to False
        :type negative: bool

        Example:

        .. code-block:: python3

                kameleoon_client.add_data(visitor_code, Conversion(1, 100.0))

        """
        super().__init__()
        self.goal_id = goal_id
        self.revenue = revenue
        self.negative = negative
        self._instance: DataType = DataType.CONVERSION

    def obtain_full_post_text_line(self) -> str:
        # remove query_builder, it's done due due pylint issue with R0801 - duplicate_code,
        # need to update pylint and return str(QueryBuilder) straightaway
        query_builder = QueryBuilder(
            QueryParam(QueryParams.EVENT_TYPE, self.EVENT_TYPE),
            QueryParam(QueryParams.GOAL_ID, str(self.goal_id)),
            QueryParam(QueryParams.REVENUE, str(self.revenue)),
            QueryParam(QueryParams.NEGATIVE, "true" if self.negative else "false"),
            QueryParam(QueryParams.NONCE, self._nonce),
        )
        return str(query_builder)
