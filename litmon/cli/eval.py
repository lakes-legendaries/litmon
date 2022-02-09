"""Score journal articles in eval set"""

from numpy import ones, sort
from pandas import DataFrame, ExcelWriter, read_csv

from litmon.model import ArticleScorer
from litmon.utils import Azure, cli, drange


class ModelUser:
    """Use trained :class:`litmon.model.ArticleScorer` to score articles

    Articles with high scores are relevant to the mission of the Methuselah
    Foundation.

    Top-scoring articles are written to excel files.

    Parameters
    ----------
    date_range: str
        months to use for training. Format: YYYY/mm-YYYY/mm
    count: int, optional, default=30
        Write the top-scoring :code:`count` articles to file.
        If :code:`thresh` is specified, then this is ignored.
    dbase_dir: str, optional, default='data'
        directory to load database files from.
        :code:`dbase_fname=f'{dbase_dir}/{year}-{month:02d}{dbase_suffix}.csv'`
    dbase_suffix: str, optional, default='-eval'
        suffix for each database file. See :code:`dbase_dir`
    include_missed: bool, optional, default=True
        whether missing articles should be included in the output
        :code:`*.xlsx` file. The default value for this is expected to change
        in the future.
    model_fname: str, optional, default='data/model'
        Input filename for saved trained model. This should NOT have a file
        extension, because a :code:`model_fname.bin` and a
        :code:`model_fname.pickle` file are loaded in.
    results_dir: str, optional, default='data'
        directory to write results to.
        :code:`results_fname=f'{results_dir}/{year}-{month:02d}{results_suffix}.xlsx'`
    results_suffix: str, optional, default='-results'
        suffix for each results file. See :code:`results_dir`
    thresh: float, optional, default=None
        If specified, then write all articles with score >= :code:`thresh`
        (instead of the top :code:`count` articles)
    write_csv: bool, optional, default=False
        write results to csv file. fname will be :code:`results_fname`, as
        listed in :code:`results_dir`, but with a :code:`.csv` extension.
    write_xlsx: bool, optional, default=Treu
        write results to xlsx file
    """
    def __init__(
        self,
        /,
        date_range: str,
        *,
        count: int = 30,
        dbase_dir: str = 'data',
        dbase_suffix: str = '-eval',
        include_missed: bool = True,
        model_fname: str = 'data/model',
        results_dir: str = 'data',
        results_suffix: str = '-results',
        thresh: float = None,
        write_csv: bool = False,
        write_xlsx: bool = True,
    ):
        # load in model
        Azure.download(f'{model_fname}.bin', private=True)
        Azure.download(f'{model_fname}.pickle', private=True)
        model = ArticleScorer.load(model_fname)

        # set flags
        use_count = not thresh

        # process one month at a time
        for year, month in drange(date_range):

            # load in data
            dbase_fname = \
                f'{dbase_dir}/{year:4d}-{month:02d}{dbase_suffix}.csv'
            Azure.download(dbase_fname, private=True)
            articles = read_csv(dbase_fname)

            # add feedback column
            articles.loc[:, 'feedback'] = \
                ['' for _ in range(articles.shape[0])]

            # score each article
            scores = model.predict(articles)
            articles.loc[:, 'score'] = scores

            # get indices of top-scoring articles
            if use_count and count >= articles.shape[0]:
                keep_me = ones(articles.shape[0], dtype=bool)
            else:
                if use_count:
                    thresh = sort(scores)[-count]
                keep_me = scores >= thresh

            # extract top-scoring articles
            top_scoring = \
                self.__class__.rearrange(articles.iloc[keep_me, :])

            # write csv results
            if write_csv:
                results_fname = \
                    f'{results_dir}/{year}-{month:02d}{results_suffix}.csv'
                top_scoring.to_csv(results_fname)

            # done, if not writing xlsx
            if not write_xlsx:
                continue

            # extract missed articles
            if include_missed:
                is_missed = articles['label'].to_numpy() * ~keep_me
                missed = self.__class__.rearrange(articles.iloc[is_missed, :])

            # open xlsx file
            results_fname = \
                f'{results_dir}/{year}-{month:02d}{results_suffix}.xlsx'
            writer = ExcelWriter(results_fname, engine='xlsxwriter')

            # declare cell formats
            cell_format = writer.book.add_format()
            cell_format.set_text_wrap()
            cell_format.set_align('top')
            cell_format.set_align('left')

            # process args
            sheet_names = ['Top-Scoring Articles']
            dfs = [top_scoring]
            if include_missed:
                sheet_names.append('Missed Articles')
                dfs.append(missed)

            # write dfs to excelt
            for sheet_name, df in zip(sheet_names, dfs):

                # write data
                df.to_excel(
                    writer,
                    sheet_name=sheet_name,
                    index=False,
                )

                # format data
                worksheet = writer.sheets[sheet_name]
                worksheet.set_column(0, 2, 75, cell_format)
                worksheet.set_column(6, 7, 75, cell_format)
                worksheet.set_column(8, 10, 30, cell_format)
                worksheet.set_column(11, 13, 75, cell_format)
                for row in range(1, df.shape[0]):
                    worksheet.set_row(row, 200)

            # save xlsx file
            writer.save()

    @classmethod
    def rearrange(cls, df: DataFrame, /) -> DataFrame:
        """Rearrange columns, sort by scores

        Parameters
        ----------
        df: DataFrame
            input df

        Returns
        -------
        df: DataFrame
            output df
        """
        order = [
            'title',
            'abstract',
            'keywords',
            'score',
            'label',
            'feedback',
            'journal',
            'authors',
            'publication_date',
            'doi',
            'pubmed_id',
            'methods',
            'results',
            'conclusions',
            'copyrights',
        ]
        return df[order].sort_values(by='score', ascending=False)


# command-line interface
if __name__ == '__main__':
    config = cli(
        cls='litmon.cli.eval.ModelUser',
        description='Score journal articles in eval set',
        default=['eval_dates'],
    )
    ModelUser(**config)
