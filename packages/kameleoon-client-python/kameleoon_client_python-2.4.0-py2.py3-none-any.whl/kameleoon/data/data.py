""" Kameleoon data module"""
from enum import IntEnum
from typing import Any, Dict

from kameleoon.network.post_body_line import PostBodyLine, get_nonce


class DataType(IntEnum):
    """Data types"""

    CUSTOM_DATA = 0
    BROWSER = 1
    CONVERSION = 2
    DEVICE = 3
    PAGE_VIEW = 4


class Data(PostBodyLine):
    """Base data class"""

    def __init__(self) -> None:
        super().__init__()
        self._nonce: str = get_nonce()
        self.sent: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert class instance to dict"""
        return self.__dict__

    def obtain_full_post_text_line(self) -> str:
        """
        obtain full post text line
        :return:
        """
        raise NotImplementedError
