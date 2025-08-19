
from functools import cached_property
from typing import (Dict, Final, Iterator, List, Self, Tuple, Union)

import pandas


class Model:
    """
    A base class for models that can be used to represent financial data.
    """

    def __init__(
            self: Self,
            timestamp: Union[pandas.Timestamp, int],
            open: float,
            high: float,
            low: float,
            close: float,
            volume: float,
        ) -> None:

        """
        Initializes the attributes of the 'Model' OHCLV object with the given
        parameters.
        """

        if isinstance(timestamp, int):
            self._t = pandas.Timestamp(timestamp, unit='ms')
        else:
            self._t = timestamp

        self._o = open
        self._h = high
        self._l = low
        self._c = close
        self._v = volume

    def __iter__(self: Self) -> Iterator:
        """
        Returns an iterator over the 'Model' object.
        """

        yield self.timestamp
        yield self.open
        yield self.high
        yield self.low
        yield self.close
        yield self.volume

    @cached_property
    def timestamp(self: Self) -> pandas.Timestamp:
        """
        Returns the timestamp of the 'Model' object.
        """

        return self._t

    @cached_property
    def open(self: Self) -> float:
        """
        Returns the open price of the 'Model' object.
        """

        return self._o

    @cached_property
    def high(self: Self) -> float:
        """
        Returns the high price of the 'Model' object.
        """

        return self._h

    @cached_property
    def low(self: Self) -> float:
        """
        Returns the low price of the 'Model' object.
        """

        return self._l

    @property
    def close(self: Self) -> float:
        """
        Returns the close price of the 'Model' object.
        """

        return self._c

    @cached_property
    def volume(self: Self) -> float:
        """
        Returns the volume of the 'Model' object.
        """

        return self._v

    @staticmethod
    def from_dict(d: Dict):
        """
        Creates an 'Model' object from a Dict.
        """

        return Model(
            timestamp=d['t'],
            open=d['o'],
            high=d['h'],
            low=d['l'],
            close=d['c'],
            volume=d['v']
        )

    def to_dict(self: Self) -> Dict:
        """
        Converts the 'Model' object to a Dict.
        """

        return {
            't': pandas.Timestamp(self.timestamp, unit='s'),
            'o': self.open,
            'h': self.high,
            'l': self.low,
            'c': self.close,
            'v': self.volume,
        }

class OHLCV(Model):
    """
    The OHLCV (Open, High, Low, Close, Volume) class for tracks historical
    financial  data of an equity by it's timestamp, symbol, and OHLCV values.
    """

    def __init__(
            self: Self,
            timestamp: Union[pandas.Timestamp | int],
            symbol: str,
            open: float,
            high: float,
            low: float,
            close: float,
            volume: float,
        ) -> None:

        self._s = symbol

        super().__init__(
            timestamp=timestamp,
            open=open,
            high=high,
            low=low,
            close=close,
            volume=volume
        )

    @cached_property
    def symbol(self: Self) -> str:
        """
        Returns the symbol of the OHLCV object.
        """

        return self._s

    def __repr__(self: Self) -> str:
        """
        Returns a string representation of the OHLCV object.
        """

        return f"OHLCV(timestamp={self.timestamp}, symbol='{self.symbol}', open={self.open}, high={self.high}, low={self.low}, close={self.close}, volume={self.volume})"

    @staticmethod
    def from_tuple(t: Tuple[pandas.Timestamp, str, float, float, float, float, float]):
        """
        Creates an OHLCV object from a Tuple.
        """

        return OHLCV(
            timestamp=pandas.Timestamp(t[0], unit='s'),
            symbol=t[1],
            open=t[2],
            high=t[3],
            low=t[4],
            close=t[5],
            volume=t[6],
        )

    def to_tuple(self: Self) -> Tuple[pandas.Timestamp, str, float, float, float, float, float]:
        """
        Converts the OHLCV object to a Tuple.
        """

        return (
            self.timestamp.timestamp(),
            self.symbol,
            self.open,
            self.high,
            self.low,
            self.close,
            self.volume
        )
