"""Fit ML model"""

from pandas import DataFrame, read_csv

from litmon.model import ArticleScorer
from litmon.utils import Azure, cli, drange


class ModelFitter:
    """Train :class:`litmon.model.ArticleScorer` on fitting articles

    Parameters
    ----------
    date_range: str
        months to use for training. Format: YYYY/mm-YYYY/mm
    dbase_dir: str, optional, default='data'
        directory to load database files from.
        :code:`dbase_fname=f'{dbase_dir}/{year}-{month:02d}{dbase_suffix}.csv'`
    dbase_suffix: str, optional, default='-fit'
        suffix for each database file. See :code:`dbase_dir`
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
        date_range: str,
        *,
        dbase_dir: str = 'data',
        dbase_suffix: str = '-fit',
        model_fname: str = 'data/model',
        **kwargs
    ):

        # load in data
        data = DataFrame()
        for year, month in drange(date_range):
            dbase_fname = \
                f'{dbase_dir}/{year:4d}-{month:02d}{dbase_suffix}.csv'
            Azure.download(dbase_fname, private=True)
            data = data.append(read_csv(dbase_fname))

        # fit model
        model = ArticleScorer(**kwargs).fit(data)

        # save model
        model.save(model_fname)


# command-line interface
if __name__ == '__main__':
    config = cli(
        cls='litmon.cli.fit.ModelFitter',
        description='Fit ML model',
        default=['fit_dates', 'fit'],
    )
    ModelFitter(**config)
