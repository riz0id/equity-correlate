
import numpy
import pandas as pd

from garch import *
from garch_loss import *
from dcc import *
from dcc_loss import *

from argparse import (ArgumentParser, ArgumentTypeError)
from datetime import (datetime, timedelta)
from polygon import (RESTClient)


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
        api_key: str,
        tickers: list[str],
        start: datetime,
        end: datetime,
        column: str = 'close',
        timespan: str = 'day'
    ):

    client = RESTClient(api_key=api_key)

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

        for i, record in enumerate(records):
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
            data=arr,
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
        '--api-key',
        help="""
            (Optional). The Polygon.io API key to use for the query. If not
            specified, then the $POLYGON_API_KEY environment variable will be
            used.
        """,
        metavar='KEY',
        type=str,
        required=True,
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
        '--column',
        default='close',
        help="""
            (Optional). The column to use for the correlation calculation. Defaults
            to 'close' if not specified.
        """,
        metavar='COLUMN',
        type=str,
        required=False,
        choices=[
            'open',
            'high',
            'low',
            'close',
            'volume'
        ],
    )

    parser.add_argument(
        '--max-iterations',
        default=None,
        help="""
            (Optional). The number of GARCH iterations to perform. Defaults to 1
            if not specified.
        """,
        metavar='N',
        type=int,
        required=False,
    )

    parser.add_argument(
        '--method',
        default='SLSQP',
        help="""
            (Optional). The optimization method to use. Defaults to 'SLSQP' if not
            specified.
        """,
        metavar='METHOD',
        required=False,
        choices=[
            'COBYLA',
            'COBYQA',
            'SLSQP',
            'trust-constr'
        ],
    )

    parser.add_argument(
        '--stopping_early',
        default=True,
        help="""
            (Optional). Whether to stop early if the loss does not improve.
            Defaults to True if not specified.
        """,
        metavar='BOOLEAN',
        type=bool,
        required=False,
    )

    parser.add_argument(
        '--p',
        default=1,
        help="""
            (Optional). The order of GARCH model to use. Defaults to 1 if not
            specified.
        """,
        metavar='N',
        type=int,
        required=False,
    )

    parser.add_argument(
        '--q',
        default=1,
        help="""
            (Optional). The order of GARCH model to use. Defaults to 1 if not
            specified.
        """,
        metavar='N',
        type=int,
        required=False,
    )

    parser.add_argument(
        'tickers',
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

    aggs = get_aggs(
        api_key=args.api_key,
        tickers=args.tickers,
        start=args.start,
        end=args.end,
        timespan='day',
        column=args.column,
    )

    for i, this_ticker in enumerate(args.tickers):
        ticker_data = aggs[i]

        for v, other_ticker in enumerate(args.tickers):
            if i != v:
                new_this_data, new_that_data = ticker_data.align(aggs[v], join='inner', axis=0)
                aggs[i] = new_this_data
                aggs[v] = new_that_data

    def garch_model(i: int, ticker: str) -> tuple[float, float]:
        aggs[i].to_csv(f'data/{ticker}.csv')

        model = GARCH(
            max_iterations=args.max_iterations,
            p=args.p,
            q=args.q,
            method=args.method,
            stopping_early=args.stopping_early,
        )

        returns = np.log(aggs[i][args.column]).diff().dropna()
        returns = returns.iloc[::-1]

        model.fit(returns)

        sigma   = model.sigma(returns)
        epsilon = returns / sigma

        return model.theta, sigma, epsilon

    results = {}

    for i, s1 in enumerate(args.tickers):
        results[i] = {}

        for j, s2 in enumerate(args.tickers):
            if s1 != s2 and i > j:
                s1_theta, _, s1_epsilon = garch_model(i, s1)
                s2_theta, _, s2_epsilon = garch_model(j, s2)

                print(s1_epsilon)
                epsilon = np.array([s1_epsilon, s2_epsilon])

                dcc_model = DCC()
                dcc_model.fit(epsilon)

                result = dcc_model.ab

                print(f"{s1}: {s1_theta}")
                print(f"{s2}: {s2_theta}")
                print(args.tickers)
                print(result)

                results[i][j] = result[0]
                results[j][i] = result[1]

    print(results)
    df_results = pd.DataFrame(data=results, columns=args.tickers)
    df_results.to_csv('data/results.csv')

    print("finished...")

if __name__ == '__main__':
    main()