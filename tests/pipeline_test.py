from glob import glob
from os import remove

from pandas import read_csv
import yaml

from litmon import DBaseBuilder, PositiveQuerier


def test():

    # delete temporary files after test
    try:

        # load in standard config
        config = yaml.safe_load(open('config/litmon.yaml', 'r'))

        # get positives
        pos_fname = 'tests/pipeline_pos.csv'
        PositiveQuerier(
            fname=pos_fname,
            pmids=[
                '24024165',
                '24025336',
            ],
            email=config['user']['email'],
            tool=config['user']['tool'],
        )

        # check positives
        data = read_csv(pos_fname)
        assert(data.shape[0] == 2)
        assert((data['publication_date'] == '2013-09-12').sum() == 1)
        assert((data['publication_date'] == '2013-09-13').sum() == 1)

        # build database
        dbase_fname = 'tests/pipeline_dbase.csv'
        DBaseBuilder(
            dbase_fname=dbase_fname,
            pos_fname=pos_fname,
            query=config['query'],
            email=config['user']['email'],
            log_fname=None,
            tool=config['user']['tool'],
        )

        # check database
        data = read_csv(dbase_fname)
        assert(data.shape[0] > 100)
        assert(data['label'].sum() == 2)
        assert(data['index'].max() + 1 == data.shape[0])

        # split data
        pass

    finally:
        for file in glob('tests/*.csv'):
            remove(file)


if __name__ == '__main__':
    test()
