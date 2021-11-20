"""Module for parsing dates"""

from __future__ import annotations

import re


def drange(datestr: str, /) -> list[tuple(int, int)]:
    """Transform datestring into list of dates

    Each date covered in datestr is unpacked so that its year/month is
    listed. E.g.

    .. code-block:: python

        cls.drange('2014/11-2015/01') == [
            (2014, 11),
            (2014, 12),
            (2015, 1),
        ]

    Parameters
    ----------
    datestr: str
        dates, in format YYYY/mm-YYYY/mm

    Returns
    -------
    drange: list[tuple(int, int)]
        list of year/month combos for each year/month in :code:`datestr`.
        :code:`drange[0]=(year, month)` for the first month covered in
        datestr.
    """

    # parse arguments
    try:
        first_year, first_month, final_year, final_month = \
            (int(x) for x in re.findall(r'\d+', datestr))
    except Exception:
        raise ValueError('Required datestr format is YYYY/mm-YYYY/mm')

    # make range
    drange = []
    (year, month) = (first_year, first_month)
    while (now := (year, month)) <= (final_year, final_month):

        # add to list
        drange.append(now)

        # increment month
        if month < 12:
            month += 1
        else:
            month = 1
            year += 1

    # return
    return drange
