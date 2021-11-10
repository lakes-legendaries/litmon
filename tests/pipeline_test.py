from glob import glob
from os import remove
from random import seed

from pandas import read_csv
import yaml

from litmon import DBaseBuilder, PositiveQuerier, Splitter


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
        data = read_csv(config['fname']['pos'])
        assert(data.shape[0] == 2)
        assert((data['publication_date'] == '2013-09-12').sum() == 1)
        assert((data['publication_date'] == '2013-09-13').sum() == 1)

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
        data = read_csv(config['fname']['dbase'])
        assert(data.shape[0] > 100)
        assert(data['label'].sum() == 2)
        assert(data['index'].max() + 1 == data.shape[0])

        # split data
        Splitter(
            dbase_fname=config['fname']['dbase'],
            fit_fname=config['fname']['fit'],
            eval_fname=config['fname']['eval'],
            cutoff_date='2013-09-13',
        )

        # check fit set
        data = read_csv(config['fname']['fit'])
        assert(data['label'].sum() == 1)
        assert(data.shape[0] <= 6)
        assert(all(data['publication_date'] == '2013-09-12'))

        # check fit set
        data = read_csv(config['fname']['eval'])
        assert(data['label'].sum() == 1)
        assert(data.shape[0] > 100)
        assert(all(data['publication_date'] == '2013-09-13'))

    finally:
        for file in glob('tests/*.csv'):
            remove(file)


if __name__ == '__main__':
    test()
