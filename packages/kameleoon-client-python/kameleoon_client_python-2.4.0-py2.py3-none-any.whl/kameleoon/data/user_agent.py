"""User Agent data"""

from kameleoon.data.data import Data


# pylint: disable=W0223,W0231
class UserAgent(Data):
    """User Agent data"""

    def __init__(self, value: str) -> None:
        """
        :param value: User Agent header value which would be used for tracking requests

        Example:
        .. code-block:: python3
                kameleoon_client.add_data(visitor_code, UserAgent('TestUserAgent'))
        """
        self.value = value

    def get_value(self) -> str:
        """
        return user agent value
        :return:
        """
        return self.value
