from os import remove

from pandas import DataFrame

from litmon import ArticleScorer


def get_fit_data() -> DataFrame:
    return DataFrame([
        ['hello', 'mike man', 0],
        ['hello', 'dinosaur dude', 2],
        ['hello', 'dude', 2],
        ['hello', 'mike dinosaur', 1],
    ], columns=['1', '2', 'label'])


def get_eval_data() -> DataFrame:
    return DataFrame([
        ['hello', 'mike'],
        ['hello', 'dinosaur'],
        ['hello', 'man'],
        ['hello', 'dude'],
    ], columns=['1', '2'])


def test_scoring():

    # temporary file
    dbase_fname = 'tests/dbase_fit.csv'

    # run test
    try:
        # create fit dataset
        get_fit_data().to_csv(dbase_fname)

        # train model
        model = ArticleScorer(use_cols=['1', '2']).fit(dbase_fname)

        # create eval dataset
        get_eval_data().to_csv(dbase_fname)

        # predict scores
        scores = model.predict(dbase_fname)

        # check results
        assert(scores[2] < scores[0] < scores[1] < scores[3])

    # remove temporary file
    finally:
        remove(dbase_fname)


def test_io():

    # temporary files
    dbase_fit_fname = 'tests/dbase_fit.csv'
    dbase_eval_fname = 'tests/dbase_eval.csv'
    model_fname = 'tests/model'

    # run test
    try:
        # create datasets
        get_fit_data().to_csv(dbase_fit_fname)
        get_eval_data().to_csv(dbase_eval_fname)

        # train model, get scores, save to file
        model = ArticleScorer(use_cols=['1', '2']).fit(dbase_fit_fname)
        scores = model.predict(dbase_eval_fname)
        model.save(model_fname)

        # load model from file, get scores
        model2 = ArticleScorer.load(model_fname)
        scores2 = model2.predict(dbase_eval_fname)

        # check results
        assert(len(scores) == len(scores2))
        assert((scores == scores2).all())

    # remove temporary file
    finally:
        remove(dbase_fit_fname)
        remove(dbase_eval_fname)
        remove(f'{model_fname}.bin')
        remove(f'{model_fname}.pickle')


if __name__ == '__main__':
    test_scoring()
    test_io()
