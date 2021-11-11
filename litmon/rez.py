"""Process results, write to file"""

from argparse import ArgumentParser

import numpy
from numpy import argsort, array
from pandas import DataFrame, read_csv
import yaml


class ResultsWriter:
    """Process results, write to file

    Parameters
    ----------
    eval_csv_fname: str
        Input fitting filename (csv)
    eval_scores_fname: str
        Input scores filename
    rez_fname: str
        Output results fname
    chunk_size: int
        number of articles in :code:`eval_csv_fname` to process at once
    num_write: int
        Write the top :code:`num_write` articles to file
    """
    def __init__(
        self,
        /,
        eval_csv_fname: str,
        eval_scores_fname: str,
        rez_fname: str,
        *,
        chunk_size: int = 10e3,
        num_write: int = 1000,
    ):
        # load scores
        eval_scores = numpy.load(eval_scores_fname)

        # find top-scoring articles
        order = argsort(eval_scores)[::-1]
        keep_idx = order[0: min(num_write, len(eval_scores))]

        # extract top-scoring articles
        rez = DataFrame()
        for chunk, eval_csv in enumerate(
            read_csv(
                eval_csv_fname,
                chunksize=chunk_size,
            )
        ):
            # get relative indices for articles
            idx = array(range(eval_csv.shape[0])) + chunk * chunk_size

            # get articles to extract
            extract_me = array([i in keep_idx for i in idx])

            # extract articles
            df = eval_csv.iloc[extract_me, :].reset_index(drop=True)

            # add scores
            df.loc[:, 'scores'] = eval_scores[idx[extract_me]]

            # append to df
            rez = rez.append(df)

        # write to file
        rez.to_csv(rez_fname, index=False)


# command-line interface
if __name__ == '__main__':

    # parse command-line arguments
    parser = ArgumentParser('Process results, write to file')
    parser.add_argument(
        '-c',
        '--config_fname',
        default='config/std.yaml',
        help='Configuration yaml file. '
             'See the docs for details. ',
    )
    args = parser.parse_args()

    # load configuration
    config = yaml.safe_load(open(args.config_fname, 'r'))

    # write results
    ResultsWriter(
        eval_csv_fname=config['fname']['eval_csv'],
        eval_scores_fname=config['fname']['eval_scores'],
        rez_fname=config['fname']['rez'],
        **config['kwargs']['rez'],
    )
