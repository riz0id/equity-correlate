
# import json
# import logging
# import matplotlib.pyplot as plt
# import mplfinance as mpf
# import numpy
# import pandas as pd

from args import (parse_args)
from garch import *
from garch_loss import *
from dcc import *
from dcc_loss import *
from matplotlib import pyplot as plt
from util import *

import util.database as database
import sqlite3

# from argparse import (ArgumentParser, ArgumentTypeError)
# from datetime import (datetime, timedelta)
# from functools import reduce
# from polygon import (RESTClient)

# def date_range_list(start_date: datetime, end_date: datetime) -> list[datetime]:
#     """
#     Generates a list of dates between start_date and end_date (inclusive).
#     The start_date and end_date should be datetime.date objects.
#     """

#     curr_date = start_date
#     date_list = []

#     while curr_date <= end_date:
#         date_list.append(curr_date)
#         curr_date += timedelta(days=1)

#     return date_list

# def is_weekday(date: datetime) -> bool:
#     """
#     Checks if the given date is a weekday (Monday to Friday).
#     """

#     return 0 <= date.weekday() <= 4

def plot_data(dataframe: pd.DataFrame) -> NoReturn:
    """
    Plot financial returns.
    """

    plt.figure(figsize=(12, 6))
    plt.plot(dataframe, label='Graph', linewidth=2)
    plt.title('Title Label')
    plt.xlabel('Date')
    plt.ylabel('Returns')
    plt.legend(dataframe.columns)
    plt.show()

def main():
    args = parse_args()

    logger.debug(f"{__name__}: {args}")

    # Set the logging level based on the verbosity argument.
    if args.verbosity == 'debug':
        logger.setLevel(logging.DEBUG)
        handler.setLevel(logging.DEBUG)
    elif args.verbosity == 'info':
        logger.setLevel(logging.INFO)
        handler.setLevel(logging.INFO)
    else:
        raise ValueError(f"Invalid verbosity level: {args.verbosity}. Must be 'debug' or 'info'.")

    database.init()

    client = PolygonClient(api_key=args.api_key)

    for series in client.fetch(tickers=args.tickers, t0=args.start, t1=args.end):
        epsilon = []

        for ticker in args.tickers:
            returns = series[ticker]

            model = GARCH(
                max_iterations=args.max_iterations,
                p=args.p,
                q=args.q,
                method=args.method,
                stopping_early=args.stopping_early,
            )

            model.fit(returns)

            epsilon.append(returns / model.sigma(returns))

        epsilon = np.array(epsilon)

        dcc_model = DCC(
            max_iterations=args.max_iterations,
            method=args.method,
            stopping_early=args.stopping_early,
            n=len(args.tickers),
        )

        dcc_model.fit(epsilon)

        result = dcc_model.ab
        print(result)





    # epsilon = []

    # for ticker in args.tickers:
    #     returns = series[ticker]

    #     model = GARCH(
    #         max_iterations=args.max_iterations,
    #         p=args.p,
    #         q=args.q,
    #         method=args.method,
    #         stopping_early=args.stopping_early,
    #     )

    #     model.fit(returns)

    #     epsilon.append(returns / model.sigma(returns))

    # model = DCC(
    #     max_iterations=args.max_iterations,
    #     method=args.method,
    #     stopping_early=args.stopping_early,
    #     n=len(args.tickers),
    # )

    # model.fit(np.array(epsilon))

    # result = model.ab

    # print(result)




    # for ticker in args.tickers:
    #     logger.info(f"fetching {ticker} from {args.start} to {args.end}")




    # dataframe = get_aggregates(
    #     api_key=args.api_key,
    #     tickers=args.tickers,
    #     t0=args.start,
    #     t1=args.end,
    #     dt=Timespan(args.timespan)
    # )

    # Export data used to fit GARCH models to a CSV file for inspection or
    # further use.
    # dataframe.to_csv('data/aggregates.csv')

    # greeks = []
    # ntickers = len(args.tickers)

    # for ticker in args.tickers:
    #     returns = dataframe[ticker]

    #     model = GARCH(
    #         max_iterations=args.max_iterations,
    #         p=args.p,
    #         q=args.q,
    #         method=args.method,
    #         stopping_early=args.stopping_early,
    #     )

    #     model.fit(returns)

    #     sigma = model.sigma(returns)
    #     epsilon = returns / sigma

    #     greeks.append(epsilon.array)

    # # greeks = pd.concat(greeks, keys=args.tickers, axis=1)
    # greeks = np.array(greeks)

    # dcc_model = DCC(
    #     max_iterations=args.max_iterations,
    #     method=args.method,
    #     stopping_early=args.stopping_early,
    #     n=ntickers,
    # )

    # dcc_model.fit(greeks)

    # result = dcc_model.ab

    # # dump = json.dumps(greeks, indent=4, separators=(',', ': '), sort_keys=True)
    # #
    # # with open('data/greeks.json', 'w') as file:
    # #     file.write(dump)


if __name__ == '__main__':
    main()