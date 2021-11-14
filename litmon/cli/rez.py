"""Process results, write to file"""

import numpy
from numpy import argsort, array
from pandas import DataFrame, ExcelWriter, read_csv

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
    chunk_size: int
        number of articles in :code:`eval_csv_fname` to process at once
    num_write: int
        Write the top :code:`num_write` articles to file
    """
    def __init__(
        self,
        /,
        dbase_fname: str = 'data/dbase_eval.csv',
        scores_fname: str = 'data/scores.npy',
        rez_fname: str = 'data/results',
        *,
        chunk_size: int = 10e3,
        num_write: int = 30,
    ):

        # load scores
        scores = numpy.load(scores_fname)

        # get indices of top-scoring articles
        order = argsort(scores)[::-1]
        keep_idx = order[0: min(num_write, len(scores))]

        # extract top-scoring articles
        rez = DataFrame()
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
            mdf.loc[:, 'scores'] = scores[idx[fn]]
            mdf.loc[:, 'label2'] = ['' for _ in range(mdf.shape[0])]

            # append dfs
            rez = rez.append(top_df)
            missed = missed.append(mdf)

        # write results to csv file
        rez.to_csv(f'{rez_fname}.csv', index=False)

        # rearrange columns
        rez = ResultsWriter.rearrange(rez)
        missed = ResultsWriter.rearrange(missed)

        # write results to xlsx file
        writer = ExcelWriter(f'{rez_fname}.xlsx', engine='xlsxwriter')
        rez.to_excel(writer, sheet_name='Top-Scoring Articles', index=False)
        missed.to_excel(writer, sheet_name='Missed Articles', index=False)
        cell_format = writer.book.add_format()
        cell_format.set_text_wrap()
        cell_format.set_align('top')
        cell_format.set_align('left')
        # cell_format.set_align('hleft')
        for worksheet in writer.sheets.values():
            worksheet.set_column(0, 2, 75, cell_format)
            worksheet.set_column(6, 7, 75, cell_format)
            worksheet.set_column(8, 10, 30, cell_format)
            worksheet.set_column(11, 13, 75, cell_format)
            for row in range(1, max(rez.shape[0], missed.shape[0])):
                worksheet.set_row(row, 200)
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
