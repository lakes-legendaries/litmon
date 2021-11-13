from os import remove

from pandas import read_csv

from litmon import PositiveQuerier


def test():

    # temporary files
    pmids_fname = 'tests/pmids.txt'
    pos_fname = 'tests/positive_querier.csv'

    # delete temp files after test
    try:

        # write positives file to disk
        with open(pmids_fname, 'w') as file:
            print('24024165', file=file)
            print('24025336', file=file)

        # get positives
        PositiveQuerier(
            pmids_fname=pmids_fname,
            pos_fname=pos_fname,
            email='mike@lakeslegendaries.com',
            tool='org.mfoundation.litmon',
        )

        # check positives
        pos_data = read_csv(pos_fname)
        assert(pos_data.shape[0] == 2)
        assert((pos_data['publication_date'] == '2013-09-12').sum() == 1)
        assert((pos_data['publication_date'] == '2013-09-13').sum() == 1)

    # clean up
    finally:
        remove(pmids_fname)
        remove(pos_fname)


if __name__ == '__main__':
    test()
