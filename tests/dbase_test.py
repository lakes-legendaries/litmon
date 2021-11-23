from os import remove
from random import seed

from pandas import read_csv

from litmon.cli import DBaseBuilder


def test():

    # set seed
    seed(271828)

    # query
    query = """
        (english[la] OR hasabstract)
        AND
        (
        biogeront*
        OR "regenerative medicine"
        OR "tissue engineering"
        OR oxystero*
        OR "7-ketocholesterol"
        OR lipofus*
        OR aging
        OR ageing
        OR mitochondri*
        OR lysosom*
        OR intein*
        OR telomer*
        OR longevity
        OR glycation
        OR (aggregat* NOT platelet)
        OR amyloid*
        OR synuclein
        OR ("neurofibrillary tangles")
        OR nft
        OR nfts
        OR ("lewy bodies")
        OR ("inclusion bodies")
        OR autophag*
        OR immunosenescence
        OR (integrase* NOT HIV)
        OR (plasma AND redox)
        )
        AND
        (2007 : 2025[dp])
    """

    # filenames
    pmids_fname = 'data/pmids-test.txt'
    dbase_fname = 'data/2013-09-test.csv'

    # delete temporary files after test
    try:

        # write pmids to file
        with open(pmids_fname, 'w') as file:
            print('24024165', file=file)
            print('24025336', file=file)

        # build fit database
        DBaseBuilder(
            query=query,
            date_range='2013/09-2013/09',
            balance_ratio=3,
            dbase_suffix='-test',
            pmids_fname=pmids_fname,
            verbose=False,
            email='mike@lakeslegendaries.com',
            tool='org.mfoundation.litmon.test',
        )

        # check database
        dbase = read_csv(dbase_fname)
        assert(dbase.shape[0] < 10)
        assert(dbase['label'].sum() == 2)

    # delete temp files, restore old data directory
    finally:
        remove(pmids_fname)
        remove(dbase_fname)


if __name__ == '__main__':
    test()
