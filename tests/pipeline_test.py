from glob import glob
from os import remove
from random import seed

import numpy
from pandas import read_csv
import yaml

from litmon import DBaseBuilder, PositiveQuerier, Splitter, Vectorizer


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
            fit_fname=config['fname']['fit'],
            eval_fname=config['fname']['eval'],
            cutoff_date='2013-09-13',
        )

        # check fit set
        fit_set = read_csv(config['fname']['fit'])
        assert(fit_set['label'].sum() == 1)
        assert(fit_set.shape[0] <= 6)
        assert(all(fit_set['publication_date'] == '2013-09-12'))

        # check eval set
        eval_set = read_csv(config['fname']['eval'])
        assert(eval_set['label'].sum() == 1)
        assert(eval_set.shape[0] > 100)
        assert(all(eval_set['publication_date'] == '2013-09-13'))

        # vectorize
        Vectorizer(
            fit_ifname=config['fname']['fit'],
            fit_ofname=config['fname']['vec_fit'],
            eval_ifname=config['fname']['eval'],
            eval_ofname=config['fname']['vec_eval'],
        )

        # check vectorized fit
        vec_fit = numpy.load(config['fname']['vec_fit'])
        assert(vec_fit.shape[0] == fit_set.shape[0])
        assert(vec_fit.shape[1] == fit_set.shape[0])
        assert(vec_fit.max() <= 1 + 1e-5)
        assert(vec_fit.min() >= -1 - 1e-5)

        # check vectorized eval
        vec_eval = numpy.load(config['fname']['vec_eval'])
        assert(vec_eval.shape[0] == eval_set.shape[0])
        assert(vec_eval.shape[1] == fit_set.shape[0])
        assert(vec_eval.max() <= 1 + 1e-5)
        assert(vec_eval.min() >= -1 - 1e-5)

    finally:
        files = glob('tests/*.csv')
        files.extend(glob('tests/*.npy'))
        for file in files:
            remove(file)


if __name__ == '__main__':
    test()
