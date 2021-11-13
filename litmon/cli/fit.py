"""Fit ML model"""

from litmon.model import ArticleScorer
from litmon.utils.cli import cli


class ModelFitter:
    """Train :class:`litmon.model.ArticleScorer` on fitting articles

    Parameters
    ----------
    dbase_fname: str, optional, default='data/dbase_fit.csv'
        Input filename for training data
    model_fname: str, optional, default='data/model'
        Output filename for saving trained model to. This should NOT have a
        file extension, because a :code:`model_fname.bin` and a
        :code:`model_fname.pickle` file are created
    **kwargs: Any
        Passed to :class:`litmon.model.ArticleScorer` on :code:`__init__`
    """
    def __init__(
        self,
        /,
        dbase_fname: str = 'data/dbase_fit.csv',
        model_fname: str = 'data/model',
        **kwargs
    ):
        model = ArticleScorer(**kwargs).fit(dbase_fname)
        model.save(model_fname)


# command-line interface
if __name__ == '__main__':
    config = cli(
        cls='litmon.cli.fit.ModelFitter',
        description='Fit ML model',
        default=[],
    )
    ModelFitter(**config)
