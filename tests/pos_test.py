from os import remove

from pandas import read_csv

from litmon import PositiveQuerier


def test():

    # delete temporary file even on failure
    try:

        # hard-coded parameters
        fname = 'data/test.csv'

        # run query
        PositiveQuerier(
            fname=fname,
            pmids=[
                '10337457',
                '11891847',
            ],
            email='mike@lakeslegendaries.com',
            tool='org.mfoundation.litmon',
        )

        # load in results
        data = read_csv(fname)

        # check results
        assert(data.shape[0] == 2)

    finally:
        remove(fname)


if __name__ == '__main__':
    test()
