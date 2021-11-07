from os import remove

from pandas import read_csv
import yaml

from litmon import DBaseBuilder


def test():

    # delete temporary file even on failure
    try:

        # hard-coded parameters
        fname = 'data/test.csv'

        # run query
        DBaseBuilder(
            dbase_fname=fname,
            pos_fname='tests/sample_pos.csv',
            query=yaml.safe_load(open('config/litmon.yaml', 'r'))['query'],
            email='mike@lakeslegendaries.com',
            tool='org.mfoundation.litmon',
        )

        # load in results
        data = read_csv(fname)

        # check labels
        assert(data['label'].sum() == 2)
        assert(data.shape[0] > 2)
        assert(all(data['publication_date'] == '2013-09-26'))

    finally:
        remove(fname)


if __name__ == '__main__':
    test()
