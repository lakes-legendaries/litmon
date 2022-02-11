"""Fit ML model"""

from ezazure import Azure
from pandas import DataFrame, read_csv, read_excel

from litmon.model import ArticleScorer
from litmon.utils import cli, drange


class ModelFitter:
    """Train :class:`litmon.model.ArticleScorer` on fitting articles

    Parameters
    ----------
    date_range: str
        months to use for training. Format: YYYY/mm-YYYY/mm
    fback_range: str, optional, default=None
        additional feedback files to use in training
    dbase_dir: str, optional, default='data'
        directory to load database files from.
        :code:`dbase_fname=f'{dbase_dir}/{year}-{month:02d}{dbase_suffix}.csv'`
    dbase_suffix: str, optional, default='-fit'
        suffix for each database file. See :code:`dbase_dir`
    fback_dir: str, optional, default='data'
        directory to load feedback files from.
        :code:`fback_fname=f'{fback_dir}/{year}-{month:02d}{fback_suffix}.xlsx'`
    fback_optional: bool, optional, default=True
        if True, and feedback file cannot be found / downloaded, then skip
    fback_suffix: str, optional, default='-feedback'
        suffix for each feedback file. See :code:`fback_dir`
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
        fback_range: bool = None,
        *,
        dbase_dir: str = 'data',
        dbase_suffix: str = '-fit',
        fback_dir: str = 'data',
        fback_optional: bool = True,
        fback_suffix: str = '-feedback',
        model_fname: str = 'data/model',
        **kwargs
    ):

        # load in standard data
        data = DataFrame()
        for year, month in drange(date_range):
            dbase_fname = \
                f'{dbase_dir}/{year:4d}-{month:02d}{dbase_suffix}.csv'
            Azure().download(dbase_fname)
            data = data.append(read_csv(dbase_fname))

        # convert label to float
        data.loc[:, 'label'] = data.loc[:, 'label'].astype(float)

        # add in feedback data
        if fback_range is not None:
            for year, month in drange(fback_range):
                fback_fname = \
                    f'{fback_dir}/{year:4d}-{month:02d}{fback_suffix}.xlsx'
                try:
                    Azure().download(fback_fname)
                except FileNotFoundError as e:
                    if fback_optional:
                        continue
                    raise e
                fdata = read_excel(fback_fname)
                fdata.loc[:, 'label'] = fdata.loc[:, 'feedback']
                fdata.drop(columns=['feedback'], inplace=True)
                data = data.append(fdata)

        # drop missing label
        data.dropna(subset=['label'], inplace=True)

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
