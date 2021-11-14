from math import isclose
from os import mkdir, rename
from random import seed
from shutil import copyfile, rmtree

import numpy
from numpy import sort
from pandas import read_csv

from litmon import (
    DBaseBuilder,
    ModelFitter,
    ModelUser,
    ResultsWriter,
)


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

    # preserve existing data directory
    rename('data', 'data0')
    mkdir('data')

    # delete temporary files after test
    try:

        # write pmids to file
        with open('data/pmids.txt', 'w') as file:
            print('24024165', file=file)
            print('24025336', file=file)

        # build fit/eval databases
        DBaseBuilder(
            query=query,
            min_date='2013/09/12',
            max_date='2013/09/13',
            dbase_fname='data/dbase_fit.csv',
            email='mike@lakeslegendaries.com',
            tool='org.mfoundation.litmon',
        )
        copyfile('data/dbase_fit.csv', 'data/dbase_eval.csv')

        # check database
        dbase = read_csv('data/dbase_fit.csv')
        assert(dbase.shape[0] > 100)
        assert(dbase['label'].sum() == 2)
        assert(dbase['index'].max() + 1 == dbase.shape[0])

        # train model
        ModelFitter(chunk_size=10)

        # use model to score articles
        ModelUser()

        # check scores
        scores = numpy.load('data/scores.npy')
        assert(scores.shape[0] == dbase.shape[0])
        assert((scores[dbase['label']] >= 0.9 * scores.max()).all())

        # write results
        ResultsWriter(
            chunk_size=10,
            num_write=30,
        )

        # check results
        rez = read_csv('data/results.csv')
        assert(rez.shape[1] == dbase.shape[1] + 2)
        assert(rez.shape[0] == 30)
        assert(
            isclose(
                rez['scores'].min(),
                sort(scores)[-30],
                abs_tol=1e-6
            )
        )

    # delete temp files, restore old data directory
    finally:
        rmtree('data')
        rename('data0', 'data')


if __name__ == '__main__':
    test()
