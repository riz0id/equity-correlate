
from argparse import (ArgumentParser, ArgumentTypeError)
from datetime import (datetime, timedelta)

import logging


def is_weekend(date: datetime) -> bool:
    """
    Checks if the given date is a weekend day (Saturaday or Sunday).
    """

    return 6 <= date.weekday() <= 7

def verbosity(s: str):
    s = s.lower()
    if s == 'debug':
        return logging.DEBUG
    elif s == 'info':
        return logging.INFO
    else:
        raise ArgumentTypeError(f"Invalid verbosity level: {s}. Must be 'debug' or 'info'.")

def dateformat(s: str) -> datetime:
    """
    Parses a string in ISO-8601 format and returns a datetime object.
    """

    try:
        date = datetime.fromisoformat(s.replace('Z', '+00:00'))
        return date.replace(hour=8, minute=30, second=0, microsecond=0)
    except ValueError as e:
        raise ValueError(f"Invalid date format: {s}") from e

def parse_args() -> dict:
    """
    Create the command-line argument parser and parse arguments. Returns a
    dictionary of parsed arguments.
    """

    parser = ArgumentParser(
        prog='correlate',
        description="""
            Calculate the correlation coefficient between two or more equities
            over some specified time period with a weekly aggregation period.
        """,
        epilog="""
            Example usage:

                correlate --from 2023-01-01T00:00:00Z --to 2023-01-02T00:00:00Z BTC MSTR COIN
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
        choices=['open', 'high', 'low', 'close', 'volume'],
    )

    parser.add_argument(
        '--max-iterations',
        default=3,
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
        choices=['COBYLA', 'COBYQA', 'SLSQP', 'trust-constr'],
    )

    parser.add_argument(
        '--timespan',
        default='hour',
        help="""
            (Optional). The timespan to use for the aggregation. Defaults to 'day'
            if not specified.
        """,
        metavar='TIMESPAN',
        type=str,
        required=False,
        choices=['minute', 'hour', 'day', 'week', 'month'],
    )

    parser.add_argument(
        '--verbosity',
        default='info',
        help="""
        """,
        metavar='LEVEL',
        type=str.lower,
        required=False,
        choices=['debug', 'info'],
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

    return parser.parse_args()