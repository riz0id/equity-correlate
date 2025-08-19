
from datetime import (datetime, timedelta)
from functools import reduce
from typing import (Callable, Iterator, List, Optional, Self)


def weekly(
        t0: datetime,
        t1: datetime
    ) -> Iterator[tuple[datetime, datetime]]:

    """
    Groups a continuous 'Iterator[datetime]' into weekly 'OHLCV' objects.
    """

    def nearest_weekday(date: datetime) -> datetime:
        weekday = date.weekday()

        if weekday == 6: # If it is Saturday
            return date + timedelta(days=2) # Move to Monday
        elif weekday == 5: # If it is Sunday
            return date + timedelta(days=1) # Move to Monday'
        else:
            return date

    t0 = nearest_weekday(t0)
    t1 = nearest_weekday(t1)

    t: datetime = t0

    while t < t1:
        if t.weekday() == 4:
            yield (t0, t)

            t += timedelta(days=3) # Move to next Monday

            t0 = t
        else:
            t += timedelta(days=1)





    # while True:
    #     t0: Optional[datetime] = next(iter, None)

    #     if t0 is None:
    #         break

    #     while True:
    #         t1: Optional[datetime] = next(iter, None)

    #         if t1 is None:
    #             break

    #         weekday: int = t1.weekday()

    #         if weekday == 0: # If it's Monday
    #             t0 = t1
    #         elif weekday == 4: # If it's Friday
    #             yield (t0, t1)
    #             break

    #         continue