
import json
import numpy
import os
import pandas as pd

from garch import *
from garch_loss import *
from dcc import *
from dcc_loss import *

from argparse import (ArgumentParser, ArgumentTypeError)
from datetime import (datetime, timedelta)
from itertools import repeat
from polygon import (RESTClient)
from typing import (Optional)


def polygon_api_key() -> str:
    """
    Obtains the Polygon.io API key by reading the $POLYGON_API_KEY environment
    variable. If the $POLYGON_API_KEY variable is not set, then a ValueError
    will be raised.
    """

    result = os.getenv('POLYGON_API_KEY')

    if result is None:
        raise ValueError('no Polygon.io API present at $POLYGON_API_KEY')
    else:
        return result.strip()

def date_range_list(start_date: datetime, end_date: datetime) -> list[datetime]:
    """
    Generates a list of dates between start_date and end_date (inclusive).
    The start_date and end_date should be datetime.date objects.
    """

    date_list = []
    curr_date = start_date

    while curr_date <= end_date:
        date_list.append(curr_date)
        curr_date += timedelta(days=1)

    return date_list

def is_weekday(date: datetime) -> bool:
    """
    Checks if the given date is a weekday (Monday to Friday).
    """

    return 0 <= date.weekday() <= 4

def is_weekend(date: datetime) -> bool:
    """
    Checks if the given date is a weekend day (Saturaday or Sunday).
    """

    return 6 <= date.weekday() <= 7

def dateformat(s: str) -> datetime:
    """
    Parses a string in ISO-8601 format and returns a datetime object.
    """

    try:
        date = datetime.fromisoformat(s.replace('Z', '+00:00'))
    except ValueError as e:
        raise ValueError(f"Invalid date format: {s}") from e

    day = date.weekday()

    if day == 5:
        raise ArgumentTypeError(f"specified date {date} is a Saturday, must choose a weekday")
    elif day == 6:
        raise ArgumentTypeError(f"specified date {date} is a Sunday, must choose a weekday")
    else:
        return date

def get_aggs(
        tickers: list[str],
        start: datetime,
        end: datetime,
        timespan: str = 'hour'
    ):

    client = RESTClient(api_key=polygon_api_key())

    dfs = []

    for ticker in tickers:
        records = client.get_aggs(
            ticker=ticker,
            multiplier=1,
            adjusted=True,
            from_=start,
            to=end,
            timespan=timespan,
            sort='asc'
        )

        data = []

        for record in records:
            date = datetime.fromtimestamp(record.timestamp / 1000.0) # convert milliseconds to seconds

            if is_weekday(date):
                data.append({
                    'date': np.datetime64(f"{date.year}-{date.month:02d}-{date.day:02d}"), # record.timestamp / 1000.0,
                    'open': record.open,
                    'high': record.high,
                    'low': record.low,
                    'close': record.close,
                    'volume': record.volume,
                })

        arr = numpy.array(data)

        df = pd.DataFrame.from_records(
            data=data,
            columns=['date', 'open', 'high', 'low', 'close', 'volume'],
            index='date',
        )

        dfs.append(df)


    return dfs

timespans: list[str] = ['day', 'week', 'month']

def main():
    parser = ArgumentParser(
        prog='equity-correlate',
        description="""
            Calculate the correlation coefficient between two or more equities
            over some specified time period with a weekly aggregation period.
        """,
        epilog="""
            Example usage:

                equity-correlate --from 2023-01-01T00:00:00Z --to 2023-01-02T00:00:00Z BTC MSTR COIN
        """,
        allow_abbrev=False,
    )

    parser.add_argument(
        '--start',
        help="""
            (Required). The starting date and time for the query in ISO-8601
            format, for example '2023-01-01T00:00:00Z'.
        """,
        metavar='YYYY-mm-dd',
        required=True,
        type=dateformat,
    )

    parser.add_argument(
        '--end',
        default=datetime.now().isoformat(),
        help="""
            (Optional). The ending date and time for the query in ISO-8601
            format, for example '2023-01-01T00:00:00Z'. If no value is pass in
            via --end command-line option, then the current date and time will
            be used.
        """,
        metavar='YYYY-mm-dd',
        type=dateformat,
        required=False,
    )

    parser.add_argument(
        '--iterations',
        default=None,
        help="""
            (Option). The number of GARCH iterations to perform. Defaults to 1
            if not specified.
        """,
        metavar='N',
        type=int,
        required=False,
    )

    parser.add_argument(
        '--order',
        default=None,
        help="""
            (Option). The order of GARCH model to use. Defaults to 1 if not
            specified.
        """,
        metavar='N',
        type=int,
        required=False,
    )

    parser.add_argument(
        'tickers',
        default=None,
        help="""
            (Required). One or more tickers for equities to use in the
            calculation for correlation matrix calculation.
        """,
        nargs='+',
        metavar='TICKER(S)',
    )

    args = parser.parse_args()

    dates = []

    for date in date_range_list(args.start, args.end):
        if is_weekday(date):
            dates.append(date)

    aggs = get_aggs(tickers=args.tickers, start=args.start, end=args.end, timespan='day')

    for i, this_ticker in enumerate(args.tickers):
        ticker_data = aggs[i]

        for v, other_ticker in enumerate(args.tickers):
            if i != v:
                new_this_data, new_that_data = ticker_data.align(aggs[v], join='inner', axis=0)
                aggs[i] = new_this_data
                aggs[v] = new_that_data



    results = {}

    for i, s1 in enumerate(args.tickers):
        results[i] = {}

        for v, s2 in enumerate(args.tickers):
            if s1 != s2 and i > v:
                s1_aggs = aggs[i] # pd.read_csv('data/^GSPC.csv').set_index('Date')
                s1_aggs.to_csv(f'data/{s1}.csv', index=True)

                s1_return = np.log(s1_aggs['close']).diff().dropna() # log return of S&P500 index
                s1_return = s1_return.iloc[::-1] # the latest data should come first

                s1_model = GARCH(args.order, args.order)
                s1_model.set_loss(garch_loss_gen(args.order, args.order))
                s1_model.set_max_itr(args.iterations)
                s1_model.fit(s1_return)

                s1_theta = s1_model.get_theta()
                s1_sigma = s1_model.sigma(s1_return)
                s1_epsilon = s1_return / s1_sigma

                s2_aggs = aggs[v] # pd.read_csv('data/JPM.csv').set_index('Date')

                s2_return = np.log(s2_aggs['close']).diff().dropna() # log return of JP Morgan Chase & Co.
                s2_return = s2_return.iloc[::-1] # the latest data should come first

                s2_model = GARCH(args.order, args.order)
                s2_model.set_loss(garch_loss_gen(args.order, args.order))
                s2_model.set_max_itr(args.iterations)

                s2_model.fit(s2_return)

                s2_theta = s2_model.get_theta()
                s2_sigma = s2_model.sigma(s2_return)
                s2_epsilon = s2_return / s2_sigma

                epsilon = np.array([
                    s1_epsilon,
                    s2_epsilon
                ])

                dcc_model = DCC()
                dcc_model.set_loss(dcc_loss_gen())
                dcc_model.fit(epsilon)

                result = dcc_model.get_ab()

                print(f"{s1}: {s1_theta}")
                print(f"{s2}: {s2_theta}")
                print(args.tickers)
                print(result)

                results[i][v] = result[0]
                results[v][i] = result[1]

    print(results)
    df_results = pd.DataFrame(data=results, columns=args.tickers)
    df_results.to_csv('data/results.csv')

    print("finished...")

#     price_data[equity] = get_aggs(
#         client=client,
#         ticker=equity,
#         start=args.start,
#         end=args.end,
#         timespan='day'
#     )

#     series = {}

#     for equity, quotes in price_data.items():
#         for quote in quotes:
#             date = quote['date']

#             if series.get(date, None) is None:
#                 series[date] = []

#             series[date].append(quote['close'])

#     nequities = len(args.tickers)
#     prices = []

#     for _ in range(nequities):
#         prices.append([])

#     for date, values in series.items():

#         if len(values) == nequities:
#             for i in range(nequities):
#                 prices[i].append(values[i])

#     cor = numpy.corrcoef(prices)

#     print("correlation")
#     print(args.tickers)
#     print(cor)

#     cov = numpy.cov(prices)

#     print("covariance")
#     print(args.tickers)
#     print(cov)

# if __name__ == '__main__':
#     import asyncio
#     asyncio.run(main())

if __name__ == '__main__':
    main()