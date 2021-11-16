"""Process results, write to file"""

import numpy
from numpy import argsort, array, where
from pandas import DataFrame, ExcelWriter, read_csv
import yaml

from litmon.utils.cli import cli


class ResultsWriter:
    """Process results, write to file

    Parameters
    ----------
    dbase_fname: str, optional, default='data/dbase_eval.csv'
        Input filename for evaluation data
    scores_fname: str, optional, default='data/scores.npy'
        Output filename for model scores
    rez_fname: str, optional, default='data/results'
        Output results fname. Results will be saved to :code:`rez_fname.csv`
        and :code:`rez_fname.xlsx`
    chunk_size: int, optional, default=10E3
        number of articles in :code:`eval_csv_fname` to process at once
    count: int, optional, default=30
        Write the top-scoring :code:`count` articles to file.
        If :code:`thresh` is specified, then this is ignored.
    include_missed: bool, optional, default=True
        whether missing articles should be included in the output
        :code:`*.xlsx` file. The default value for this is expected to change
        in the future.
    thresh: float, optional, default=None
        If specified, then write all articles with score >= :code:`thresh`
        (instead of the top :code:`count` articles)
    write_stats: bool, optional, default=True
        If True, than write stats to :code:`rez_fname.stats.yaml`. Stats
        include the number of articles identified and the number of articles
        missed.
    """
    def __init__(
        self,
        /,
        dbase_fname: str = 'data/dbase_eval.csv',
        scores_fname: str = 'data/scores.npy',
        rez_fname: str = 'data/results',
        *,
        chunk_size: int = 10e3,
        count: int = 30,
        include_missed: bool = True,
        thresh: float = None,
        write_stats: bool = True,
    ):

        # load scores
        scores = numpy.load(scores_fname)

        # get indices of top-scoring articles
        if not thresh:
            order = argsort(scores)[::-1]
            keep_idx = order[0: min(count, len(scores))]
        else:
            keep_idx = where(scores >= thresh)[0]

        # extract top-scoring articles
        top_scoring = DataFrame()
        missed = DataFrame()
        dbase_iterator = read_csv(dbase_fname, chunksize=chunk_size)
        for chunk, dbase in enumerate(dbase_iterator):

            # get index of each article
            offset = chunk * chunk_size
            idx = array(range(dbase.shape[0])) + offset

            # extract articles w/ scores
            extract_me = array([i in keep_idx for i in idx])
            top_df = dbase.iloc[extract_me, :].reset_index(drop=True)
            top_df.loc[:, 'scores'] = scores[idx[extract_me].astype(int)]
            top_df.loc[:, 'label2'] = ['' for _ in range(top_df.shape[0])]

            # extract missed articles
            fn = (~extract_me * dbase['label']).to_numpy().astype(bool)
            mdf = dbase.iloc[fn, :].reset_index(drop=True)
            mdf.loc[:, 'scores'] = scores[idx[fn].astype(int)]
            mdf.loc[:, 'label2'] = ['' for _ in range(mdf.shape[0])]

            # append dfs
            top_scoring = top_scoring.append(top_df)
            missed = missed.append(mdf)

        # write results to csv file
        top_scoring.to_csv(f'{rez_fname}.csv', index=False)

        # rearrange columns
        top_scoring = ResultsWriter.rearrange(top_scoring)
        missed = ResultsWriter.rearrange(missed)

        # open xlsx file
        writer = ExcelWriter(f'{rez_fname}.xlsx', engine='xlsxwriter')

        # declare cell formats
        cell_format = writer.book.add_format()
        cell_format.set_text_wrap()
        cell_format.set_align('top')
        cell_format.set_align('left')

        # process args
        sheet_names = ['Top-Scoring Articles']
        dfs = [top_scoring]
        if include_missed:
            sheet_names.append('Missed Articlecs')
            dfs.append(missed)

        # write dfs to excelt
        for sname, df in zip(sheet_names, dfs):

            # write data
            df.to_excel(
                writer,
                sheet_name=sname,
                index=False,
            )

            # format data
            worksheet = writer.sheets[sname]
            worksheet.set_column(0, 2, 75, cell_format)
            worksheet.set_column(6, 7, 75, cell_format)
            worksheet.set_column(8, 10, 30, cell_format)
            worksheet.set_column(11, 13, 75, cell_format)
            for row in range(1, df.shape[0]):
                worksheet.set_row(row, 200)

        # save xlsx file
        writer.save()

        # write stats
        if write_stats:
            yaml.dump({
                'num_identified': top_scoring.shape[0],
                'num_found': int(top_scoring['label'].sum()),
                'num_missed': missed.shape[0],
            }, open(f'{rez_fname}.stats.yaml', 'w'))

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
            'scores',
            'label',
            'label2',
            'journal',
            'authors',
            'publication_date',
            'doi',
            'pubmed_id',
            'methods',
            'results',
            'conclusions',
            'copyrights',
            'xml',
            'index',
        ]
        return df[order].sort_values(by='scores', ascending=False)


# command-line interface
if __name__ == '__main__':
    config = cli(
        cls='litmon.rez.ResultsWriter',
        description='Process results, write to file',
        default=[],
    )
    ResultsWriter(**config)
