
from datetime import (datetime)
from polygon import RESTClient
from typing import (Any, Iterator, List, Self, Union)
import polygon
from util.ohlcv import (OHLCV)
from util.logs import (logger)
from util.time import (weekly)
from urllib3 import HTTPResponse

import pandas as pd
import util.database as database

class PolygonClient(RESTClient):
    """
    A client for interacting with the Polygon.io REST API.
    Inherits from RESTClient to provide additional functionality specific to Polygon.
    """

    def list_aggs(
            self: Self,
            ticker: str,
            t0: datetime,
            t1: datetime,
            *args: Any,
            **kwargs: Any,
        ) -> Iterator[OHLCV]:

        logger.info(f'fetching {ticker} aggregates {t0} - {t1}')

        if t0 >= t1:
            raise ValueError(f'polygon_aggregates(t0={t0}, t1={t1}, ...): t0 must be before t1')

        data = database.select_ohlcv(ticker=ticker, t0=t0, t1=t1)

        if len(data) > 0:
            logger.info(f'fetch(ticker={ticker}, t0={t0}, t1={t1}): found {len(data)} records in database')
            return data
        else:
            def to_ohlcv(agg: polygon.rest.aggs.Agg) -> OHLCV:
                return OHLCV(
                    timestamp=agg.timestamp,
                    symbol=ticker,
                    open=agg.open,
                    high=agg.high,
                    low=agg.low,
                    close=agg.close,
                    volume=agg.volume
                )

            aggs = super().list_aggs(
                ticker=ticker,
                from_=t0,
                to=t1,
                adjusted=True,
                multiplier=1,
                sort='asc',
                timespan='hour',
                **kwargs
            )

            ohlvcs = map(to_ohlcv, aggs)

            database.insert_ohlcv(objs=aggs)

            return map(to_ohlcv, aggs)

    def fetch(self: Self, tickers: List[str], t0: datetime, t1: datetime) -> Iterator[pd.DataFrame]:

        """
        TODO: docs
        """

        for i in iter(weekly(t0=t0, t1=t1)):
            dataframes = []

            for ticker in tickers:
                dataframe = pd.DataFrame.from_records(
                    data=self.list_aggs(ticker=ticker, t0=i[0], t1=i[1]),
                    index='t',
                    columns=['t', 'o', 'h', 'l', 'c', 'v']
                )

                dc = dataframe['c'].diff()
                d0 = dataframe['c'].shift(-1)

                returns = dc / d0
                returns.dropna(inplace=True)

                dataframes.append(returns)

            yield pd.concat(dataframes, axis=1, keys=tickers)


    def fetch_all(self: Self, tickers: List[str], t0: datetime, t1: datetime) -> Iterator[pd.DataFrame]:

        """
        TODO: docs
        """

        if not isinstance(tickers, list):
            raise TypeError(f"tickers must be a list, got {type(tickers)}")

        if len(tickers) == 0:
            raise ValueError("tickers list cannot be empty")

        for ticker in tickers:
            objs = self.fetch(ticker=ticker, t0=t0, t1=t1)
            yield pd.concat(objs=objs, join='outer')

    def fetch_series(self: Self, ticker: str, t0: datetime, t1: datetime) -> pd.DataFrame:
        """
        TODO: docs
        """

        dataframes: Iterator[pd.DataFrame] = self.fetch(ticker=ticker, t0=t0, t1=t1)

        # Concatenate all series into a single DataFrame.
        returns = pd.concat(map(returns, dataframes), keys=tickers, axis=1)
        returns.dropna(inplace=True)
        returns.to_csv('data/returns.csv')

        return returns
