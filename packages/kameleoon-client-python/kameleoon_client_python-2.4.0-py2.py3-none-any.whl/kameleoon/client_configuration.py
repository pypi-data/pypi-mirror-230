"""Kameleoon Client Configuration"""

from typing import Any, Dict, Optional

from kameleoon.defaults import DEFAULT_TIMEOUT_MILLISECONDS


class KameleoonClientConfiguration:
    """Client configuration which can be used instead of external configuration file"""

    # pylint: disable=R0913
    def __init__(self,
                 actions_configuration_refresh_interval: int = 60,
                 default_timeout: int = DEFAULT_TIMEOUT_MILLISECONDS,
                 visitor_data_maximum_size: int = 500,
                 environment: Optional[str] = None,
                 multi_threading: bool = False):
        self.actions_configuration_refresh_interval = actions_configuration_refresh_interval
        self.default_timeout = default_timeout
        self.visitor_data_maximum_size = visitor_data_maximum_size
        self.environment = environment
        self.multi_threading = multi_threading

    def dict(self) -> Dict[str, Any]:
        """convert object to dict"""
        return dict(vars(self))
