
from argparse import (ArgumentParser, ArgumentTypeError)
from datetime import (datetime, timedelta)
from itertools import repeat
import json
import numpy
import os
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

timespans: list[str] = ['day', 'week', 'month']

async def main():
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
        'equities',
        default=None,
        help="""
            (Required). One or more tickers for equities to use in the
            calculation for correlation matrix calculation.
        """,
        nargs='+',
        metavar='TICKER(S)',
    )

    args = parser.parse_args()

    client = RESTClient(api_key=polygon_api_key())

    dates = []

    for date in date_range_list(args.start, args.end):
        if is_weekday(date):
            dates.append(date)

    price_data = {}

    for timespan in timespans:
        for equity in args.equities:
            quotes = []

            aggs = client.get_aggs(
                ticker=equity,
                multiplier=1,
                adjusted=True,
                from_=args.start,
                to=args.end,
                timespan=timespan,
                sort='asc'
            )

            for agg in aggs:
                date = datetime.fromtimestamp(agg.timestamp / 1000.0)

                quotes.append({
                    'close': agg.close,
                    'date': datetime(date.year, date.month, date.day),
                })

            price_data[equity] = quotes

        series = {}

        for equity, quotes in price_data.items():
            for quote in quotes:
                date = quote['date']

                if series.get(date, None) is None:
                    series[date] = []

                series[date].append(quote['close'])

        nequities = len(args.equities)
        prices = []

        for _ in range(nequities):
            prices.append([])

        for date, values in series.items():

            if len(values) == nequities:
                for i in range(nequities):
                    prices[i].append(values[i])

        cor = numpy.corrcoef(prices)

        print("correlation")
        print(args.equities)
        print(cor)

        cov = numpy.cov(prices)

        print("covariance")
        print(args.equities)
        print(cov)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
