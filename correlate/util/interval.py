
from datetime import (datetime, timedelta)
from functools import cached_property
from typing import Self


class TimeInterval():
    """
    TODO: docs
    """

    def __init_(self: Self, start: datetime, end: datetime) -> None:
        self._start: datetime = start
        self._end: datetime = end

    def __repr__(self: Self) -> str:
        return f"TimeInterval(start={self.start}, end={self.end})"

    @cached_property
    def start(self: Self) -> datetime:
        """
        Returns the 'start' attribute of the 'TimeInterval'.
        """

        return self._start

    @cached_property
    def end(self: Self) -> datetime:
        """
        Returns the 'end' attribute of the 'TimeInterval'.
        """

        return self._end

