"""Split fit/eval datasets"""

from __future__ import annotations

from argparse import ArgumentParser
from random import random

from pandas import DataFrame, read_csv
import yaml

from litmon.dbase import DBaseBuilder


class Splitter:
    """Split fit/eval datasets

    Parameters
    ----------
    """
    def __init__(
        self,
        /,
        dbase_fname: str,
        fit_fname: str,
        eval_fname: str,
        cutoff_date: str,
        *,
        balance_ratio: float = 3,
        chunk_size: int = 10000,
        date_field: str = 'publication_date',
    ):

        # parse cutoff date
        cutoff_date = DBaseBuilder._get_date(cutoff_date)

        # save needed parameters
        self._chunk_size = chunk_size
        self._cutoff_date = cutoff_date
        self._date_field = date_field
        self._dbase_fname = dbase_fname
        self._fit_fname = fit_fname

        # get article count before cutoff date
        num_pos, total = self._get_counts()

        # get selection probability
        prob_incl = balance_ratio * num_pos / total

        # extract fit articles
        self._get_fitters(prob_incl)

        # extract eval articles
        eval_set = []

    def _get_counts(self) -> tuple(int, int):
        """Get count of articles before cutoff date

        Returns
        -------
        num_pos: int
            number of target articles before cutoff date
        total: int
            total number of articles before cutoff date
        """

        # initialize counts
        num_pos = 0
        total = 0

        # read database in chunks
        for articles in read_csv(
                self._dbase_fname,
                chunksize=self._chunk_size,
        ):

            # iterate through articles in chunk
            for n, (_, article) in enumerate(articles.iterrows()):

                # check if reached cutoff date
                article_date = DBaseBuilder._get_date(
                    article[self._date_field]
                )
                if article_date > self._cutoff_date:
                    break

            # update counts
            num_pos += articles['label'][0:n].sum()
            total += n + 1

            # check if reached cutoff date
            if n + 1 < self._chunk_size:
                break

        # return
        return num_pos, total

    def _get_fitters(self, prob_incl: float):
        """Get fitting articles, save to file

        Parameters
        ----------
        prob_incl: float
            probability that a non-target article should be included in the
            fitting dataset
        """

        # initialize set
        fit_set = []

        # run through database in chunks
        for articles in read_csv(
                self._dbase_fname,
                chunksize=self._chunk_size,
        ):

            # iterate through articles in chunk
            for _, article in articles.iterrows():

                # check if reached cutoff date
                article_date = DBaseBuilder._get_date(
                    article[self._date_field]
                )
                if article_date > self._cutoff_date:
                    DataFrame(fit_set).to_csv(self._fit_fname)
                    return

                # add to fitting set
                if article['label'] or random() < prob_incl:
                    fit_set.append(article)

        # save to file
        DataFrame(fit_set).to_csv(self._fit_fname)


# command-line interface
if __name__ == '__main__':

    # parse command-line arguments
    parser = ArgumentParser('Split fit/eval datasets')
    parser.add_argument(
        '-c',
        '--config_fname',
        default='config/litmon.yaml',
        help='Configuration yaml file. '
             'See the docs for details. ',
    )
    args = parser.parse_args()

    # load configuration
    config = yaml.safe_load(open(args.config_fname, 'r'))

    # create database
    Splitter(
        dbase_fname=config['fname']['dbase'],
        fit_fname=config['fname']['fit'],
        eval_fname=config['fname']['eval'],
        cutoff_date=config['dates']['eval_start'],
        **config['kwargs']['split']
    )
