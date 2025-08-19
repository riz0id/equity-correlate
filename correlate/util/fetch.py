
from datetime import (datetime)
import os
from polygon.rest.aggs import (Agg)
from typing import (Dict, Final, Iterator, List)
from urllib3 import (HTTPResponse)
from util.client import (PolygonClient)
from util.logs import (logger)

import pandas as pd

"""
Facilities for fetching equity data from Polygon.io via the Polygon API client,
and returns it as a pandas.DataFrame.
"""





# COLUMN_NAMES: Final[str] = ['timestamp', 'open', 'high', 'low', 'close', 'volume']

# class Timespan(Enum):
#     HOUR = 'hour'
#     DAY = 'day'
#     WEEK = 'week'
#     MONTH = 'month'


# def to_timestamp(ts: int) -> pd.Timestamp:
#     """
#     Convert a timestamp recording the number of miliseconds since
#     Unix epoch to a pd.Timestamp.
#     """

#     day: datetime = datetime.fromtimestamp(ts / 1e3)
#     return pd.Timestamp(day)

# tickers_filepath: Final[str] = './data/tickers.csv'

# class TickerInfo(TypedDict):
#     ticker: str
#     name: str

# def load_tickers() -> List[TickerInfo]:
#     """
#     Loads the list of tickers from the local CSV file.
#     """

#     rows = []

#     try:
#         with open(tickers_filepath, 'r') as file:
#             reader = csv.DictReader(file, fieldnames=TickerInfo.__annotations__.keys())

#             for row in reader:
#                 rows.append(TickerInfo(**row))
#     except FileNotFoundError:
#         pass

#     return rows

# def list_tickers(api_key: str) -> List[TickerInfo]:
#     """
#     Returns a list of all tickers available in the Polygon API.
#     """

#     rows = load_tickers()

#     if len(rows) > 0:
#         last_row: Optional[TickerInfo] = rows[-1]
#         last_ticker: Optional[str] = last_row.get('ticker', None)
#     else:
#         last_ticker: Optional[str] = None


#     client = PolygonClient(api_key=api_key)
#     rsp = client.list_tickers(
#         active=True,
#         sort='ticker',
#         order='asc',
#         ticker_gt=last_ticker
#     )

#     if not isinstance(rsp, list):
#         try:
#             with open('data/tickers.csv', 'w', newline='') as file:
#                 writer = csv.DictWriter(file, fieldnames=TickerInfo.__annotations__.keys())

#                 for record in rsp:
#                     row: TickerInfo = {
#                         'ticker': record.ticker,
#                         'name': record.name,
#                     }

#                     writer.writerow(row)
#                     rows.append(row)

#                 return rows
#         except KeyboardInterrupt as e:
#             file.close()

#             raise e
#         except Exception as e:
#             raise e
#     else:
#         raise ValueError(f"client.list_tickers() error: {rsp}")


# def get_aggregates(
#         api_key: str,
#         tickers: List[str],
#         t0: datetime,
#         t1: datetime,
#         dt: Timespan = Timespan.HOUR,
#     ) -> pd.DataFrame:

#     """
#     Fetches aggregate data for one or more equities from Polygon.io.
#     """

#     if len(tickers) <= 0:
#         raise ValueError("get_aggregates(tickers=[], ...): tickers must not be empty")

#     if t0 >= t1:
#         raise ValueError(f"get_aggregates(t0={t0}, t1={t1}, ...): t0 must be before t1")

#     dataframes = []

#     for ticker in tickers:

#         if isinstance(ticker, str):
#             client = PolygonClient(api_key=api_key)

#             resp = client.list_aggs(
#                 ticker=ticker,
#                 multiplier=1,
#                 adjusted=False,
#                 from_=t0,
#                 to=t1,
#                 timespan='hour',
#                 sort='asc'
#             )

#             resp = map(lambda x: {
#                 'timestamp': to_timestamp(x.timestamp),
#                 'open': float(x.open),
#                 'high': float(x.high),
#                 'low': float(x.low),
#                 'close': float(x.close),
#                 'volume': int(x.volume)
#             }, resp)

#             resp = list(filter(lambda x: 4 <= x['timestamp'].hour <= 18, resp))

#             nrows = len(resp)
#             index = np.fromiter(map(lambda x: x['timestamp'], resp), dtype='datetime64[h]', count=nrows)
#             close = np.fromiter(map(lambda x: float(x['close']), resp), dtype=float, count=nrows)

#             dataframe = pd.DataFrame(data=np.diff(np.log(close)), index=index[1:], columns=[ticker])
#             dataframe.to_csv(f'data/{ticker}.csv')
#             dataframes.append(dataframe)
#         else:
#             raise TypeError(f"get_aggregates(tickers={tickers}, ...): ticker must be a string, got {type(ticker)}")

#         time.sleep(5) # Sleep to avoid hitting rate limits

#     ret = pd.concat(dataframes, join='outer', axis=1)

#     ret.dropna(inplace=True)

#     return ret