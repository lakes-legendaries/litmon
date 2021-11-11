from glob import glob
from os import remove
from random import seed

import numpy
from pandas import read_csv
import yaml

from litmon import (
    DBaseBuilder,
    Modeler,
    PositiveQuerier,
    Splitter,
    Vectorizer,
)


def test():

    # set seed
    seed(271828)

    # delete temporary files after test
    try:

        # load in standard config
        config = yaml.safe_load(open('config/std.yaml', 'r'))

        # change filenames to write to tests folder
        for cat, fname in config['fname'].items():
            if type(fname) is not str:
                continue
            config['fname'][cat] = fname.replace('data', 'tests')

        # get positives
        PositiveQuerier(
            fname=config['fname']['pos'],
            pmids=[
                '24024165',
                '24025336',
            ],
            email=config['user']['email'],
            tool=config['user']['tool'],
        )

        # check positives
        pos_data = read_csv(config['fname']['pos'])
        assert(pos_data.shape[0] == 2)
        assert((pos_data['publication_date'] == '2013-09-12').sum() == 1)
        assert((pos_data['publication_date'] == '2013-09-13').sum() == 1)

        # build database
        DBaseBuilder(
            dbase_fname=config['fname']['dbase'],
            pos_fname=config['fname']['pos'],
            query=config['query'],
            email=config['user']['email'],
            log_fname=None,
            tool=config['user']['tool'],
        )

        # check database
        dbase = read_csv(config['fname']['dbase'])
        assert(dbase.shape[0] > 100)
        assert(dbase['label'].sum() == 2)
        assert(dbase['index'].max() + 1 == dbase.shape[0])

        # split data
        Splitter(
            dbase_fname=config['fname']['dbase'],
            fit_csv_fname=config['fname']['fit_csv'],
            eval_csv_fname=config['fname']['eval_csv'],
            cutoff_date='2013-09-13',
            balance_ratio=5,
        )

        # check fit set
        fit_csv = read_csv(config['fname']['fit_csv'])
        assert(fit_csv['label'].sum() == 1)
        assert(fit_csv.shape[0] <= 6)
        assert(all(fit_csv['publication_date'] == '2013-09-12'))

        # check eval set
        eval_csv = read_csv(config['fname']['eval_csv'])
        assert(eval_csv['label'].sum() == 1)
        assert(eval_csv.shape[0] > 100)
        assert(all(eval_csv['publication_date'] == '2013-09-13'))

        # vectorize
        Vectorizer(
            fit_csv_fname=config['fname']['fit_csv'],
            fit_npy_fname=config['fname']['fit_npy'],
            eval_csv_fname=config['fname']['eval_csv'],
            eval_npy_fname=config['fname']['eval_npy'],
        )

        # check vectorized fit
        fit_npy = numpy.load(config['fname']['fit_npy'])
        assert(fit_npy.shape[0] == fit_csv.shape[0])
        assert(fit_npy.shape[1] == fit_csv.shape[0])
        assert(fit_npy.max() <= 1 + 1e-5)
        assert(fit_npy.min() >= -1 - 1e-5)

        # check vectorized eval
        eval_npy = numpy.load(config['fname']['eval_npy'])
        assert(eval_npy.shape[0] == eval_csv.shape[0])
        assert(eval_npy.shape[1] == fit_csv.shape[0])
        assert(eval_npy.max() <= 1 + 1e-5)
        assert(eval_npy.min() >= -1 - 1e-5)

        # build ml model
        Modeler(
            fit_csv_fname=config['fname']['fit_csv'],
            fit_npy_fname=config['fname']['fit_npy'],
            eval_npy_fname=config['fname']['eval_npy'],
            eval_scores_fname=config['fname']['eval_scores'],
        )

        # check resulting scores
        eval_scores = numpy.load(config['fname']['eval_scores'])
        assert(eval_scores.shape[0] == eval_csv.shape[0])

    finally:
        files = glob('tests/*.csv')
        files.extend(glob('tests/*.npy'))
        for file in files:
            remove(file)


if __name__ == '__main__':
    test()
