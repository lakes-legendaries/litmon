"""Score journal articles in eval set"""

import numpy

from litmon.model import ArticleScorer
from litmon.utils.cli import cli


class ModelUser:
    """Use trained :class:`litmon.model.ArticleScorer` to score articles

    Articles with high scores are relevant to the mission of the Methuselah
    Foundation.

    Parameters
    ----------
    dbase_fname: str, optional, default='data/dbase_eval.csv'
        Input filename for evaluation data
    model_fname: str, optional, default='data/model'
        Input filename for saved trained model. This should NOT have a file
        extension, because a :code:`model_fname.bin` and a
        :code:`model_fname.pickle` file are loaded in.
    scores_fname: str, optional, default='data/scores.npy'
        Output filename for model scores
    """
    def __init__(
        self,
        /,
        dbase_fname: str = 'data/dbase_eval.csv',
        model_fname: str = 'data/model',
        scores_fname: str = 'data/scores.npy',
    ):
        model = ArticleScorer.load(model_fname)
        scores = model.predict(dbase_fname)
        numpy.save(scores_fname, scores)


# command-line interface
if __name__ == '__main__':
    config = cli(
        cls='litmon.cli.eval.ModelUser',
        description='Score journal articles in eval set',
        default=[],
    )
    ModelUser(**config)
