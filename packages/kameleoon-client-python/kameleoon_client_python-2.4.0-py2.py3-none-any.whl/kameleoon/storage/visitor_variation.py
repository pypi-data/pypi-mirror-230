""" Kameleoon Visitor Variation """

import time
from typing import Optional


class VisitorVariation:
    """VisitorVariation uses for saving variations for already associated visitors"""

    def __init__(self, id_: int):
        """
        VisitorVariation has an id and time when it was assigned
        """
        self.id_ = id_
        self.assignment_date = time.time()

    def is_valid(self, respool_time: Optional[int] = None):
        """
        If respool_time is after assignment_time then we say that variation
        is not valid anymore
        """
        return respool_time is None or self.assignment_date > respool_time
