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

    # create fit dataset
    fit_data = get_fit_data()

    # train model
    model = ArticleScorer(
        ml_model='sklearn.svm.LinearSVR',
        use_cols=['1', '2'],
    ).fit(fit_data)

    # create eval dataset
    eval_data = get_eval_data()

    # predict scores
    scores = model.predict(eval_data)

    # check results
    assert(scores[2] < scores[0] < scores[1] < scores[3])


def test_io():

    # temporary files
    model_fname = 'data/model-test'

    # run test
    try:
        # create datasets
        fit_data = get_fit_data()
        eval_data = get_eval_data()

        # train model, get scores, save to file
        model = ArticleScorer(
            ml_model='sklearn.svm.LinearSVR',
            use_cols=['1', '2'],
        ).fit(fit_data)
        scores = model.predict(eval_data)
        model.save(model_fname)

        # check post-save scores
        scores1 = model.predict(eval_data)
        assert(len(scores) == len(scores1))
        assert((scores == scores1).all())

        # load model from file, get scores
        model2 = ArticleScorer.load(model_fname)
        scores2 = model2.predict(eval_data)

        # check results
        assert(len(scores) == len(scores2))
        assert((scores == scores2).all())

    # remove temporary file
    finally:
        remove(f'{model_fname}.bin')
        remove(f'{model_fname}.pickle')


if __name__ == '__main__':
    test_scoring()
    test_io()
