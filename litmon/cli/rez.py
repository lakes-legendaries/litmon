"""Process results, write to file"""

import numpy
from numpy import argsort, array
from pandas import DataFrame, read_csv

from litmon.utils.cli import cli


class ResultsWriter:
    """Process results, write to file

    Parameters
    ----------
    dbase_fname: str, optional, default='data/dbase_eval.csv'
        Input filename for evaluation data
    scores_fname: str, optional, default='data/scores.npy'
        Output filename for model scores
    rez_fname: str, optional, default='data/results.csv'
        Output results fname
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
        rez_fname: str = 'data/results.csv',
        *,
        chunk_size: int = 10e3,
        num_write: int = 10,
    ):

        # load scores
        scores = numpy.load(scores_fname)

        # get indices of top-scoring articles
        order = argsort(scores)[::-1]
        keep_idx = order[0: min(num_write, len(scores))]

        # extract top-scoring articles
        rez = DataFrame()
        dbase_iterator = read_csv(dbase_fname, chunksize=chunk_size)
        for chunk, dbase in enumerate(dbase_iterator):

            # get index of each article
            offset = chunk * chunk_size
            idx = array(range(dbase.shape[0])) + offset

            # extract articles w/ scores
            extract_me = array([i in keep_idx for i in idx])
            top_df = dbase.iloc[extract_me, :].reset_index(drop=True)
            top_df.loc[:, 'scores'] = scores[idx[extract_me].astype(int)]

            # append results
            rez = rez.append(top_df)

        # write results to file
        rez.to_csv(rez_fname, index=False)


# command-line interface
if __name__ == '__main__':
    config = cli(
        cls='litmon.rez.ResultsWriter',
        description='Process results, write to file',
        default=[],
    )
    ResultsWriter(**config)
