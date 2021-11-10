from datetime import date

from pandas import DataFrame

from litmon import get_date, get_dates


def test_get_date():
    assert(get_date('2012-08-03') == date(2012, 8, 3))
    assert(get_date('2012/08/03') == date(2012, 8, 3))


def test_get_dates():
    df = DataFrame(
        [
            ['', '1991/02/12', ''],
            ['', '1992-03-02', ''],
        ],
        columns=['a', 'date', 'b'],
    )
    dates = get_dates(df['date'])
    assert(dates[0] == date(1991, 2, 12))
    assert(dates[1] == date(1992, 3, 2))


if __name__ == '__main__':
    test_get_date()
    test_get_dates()
