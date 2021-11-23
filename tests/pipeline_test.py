from os import remove

from pandas import read_csv

from litmon.cli import ModelFitter, ModelUser


def test():

    # files
    results_fname = 'data/2013-09-results-test.csv'

    # delete temporary files after test
    try:

        # train model
        ModelFitter(
            date_range='2013/09-2013/09',
            model_fname='data/model-test',
            ml_kwargs={'max_iter': 1E6},
        )

        # use model to identify top-scoring articles
        ModelUser(
            date_range='2013/09-2013/09',
            count=100,
            dbase_suffix='-fit',
            model_fname='data/model-test',
            results_suffix='-results-test',
            write_csv=True,
            write_xlsx=False,
        )

        # check results
        dbase = read_csv('data/2013-09-fit.csv')
        results = read_csv(results_fname)
        assert(results['label'].sum() == dbase['label'].sum())
        assert(results.shape[0] == 100)

    # delete temp files, restore old data directory
    finally:
        remove('data/model-test.bin')
        remove('data/model-test.pickle')
        remove(results_fname)


if __name__ == '__main__':
    test()
