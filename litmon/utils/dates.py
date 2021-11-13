"""Module for parsing dates"""

from datetime import date, datetime
from typing import Any, Union

from nptyping import NDArray
from numpy import array
from pandas import Series


def get_date(datestr: str) -> Union[date, None]:
    """Convert datestr to date

    Parameters
    ----------
    datestr: str
        date as str, in format YYYY-mm-dd or YYYY/mm/dd

    Returns
    -------
    date
        formatted date, or None if is ill-formatted
    """
    datestr = datestr.replace('/', '-')
    try:
        return datetime.strptime(datestr, '%Y-%m-%d').date()
    except Exception:
        return None


def get_dates(datestr: Series) -> NDArray[(Any,), date]:
    """Extract dates from a Series

    Parameters
    ----------
    datestr: Series of str
        dates as str, in format YYYY-mm-dd or YYYY/mm/dd.
        Any ill-formed dates will be discarded

    Returns
    -------
    NDArray
        extracted dates
    """
    dates = [
        get_date(d)
        for d in datestr
    ]
    return array([d for d in dates if d])
