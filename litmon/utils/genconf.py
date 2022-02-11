"""Generate config for live run"""

from __future__ import annotations

from datetime import datetime

import yaml


def last_month(year: int, month: int) -> tuple(int, int):
    """Rewind one month

    Parameters
    ----------
    year: int
        input year
    month: int
        input month

    Returns
    -------
    int
        year of previous month
    int
        previous month
    """
    month -= 1
    if month == 0:
        month = 12
        year -= 1
    return year, month


if __name__ == '__main__':

    # get dates
    now = datetime.now()
    this_year, this_month = last_month(now.year, now.month)
    prev_year, prev_month = last_month(this_year, this_month)
    this_datestr = f'{this_year:4d}/{this_month:02d}'
    prev_datestr = f'{prev_year:4d}/{prev_month:02d}'

    # create config
    config = yaml.safe_load(open('config/live-template.yaml', 'r'))
    config['fback']['fback_range'] += prev_datestr
    config['eval_dates']['date_range'] = f'{this_datestr}-{this_datestr}'

    # save config
    yaml.dump(config, open('config/live.yaml', 'w'))
