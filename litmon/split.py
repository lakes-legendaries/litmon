"""Split fit/eval datasets"""

from __future__ import annotations

from argparse import ArgumentParser
from random import random
from typing import Callable

from pandas import DataFrame, read_csv, Series
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
        self._num_pos = 0
        self._total = 0
        self._scan_db(Splitter._count)

        # get selection probability
        self._prob_incl = balance_ratio * self._num_pos / self._total

        # create dataset
        self._fit = []
        self._eval = []
        self._scan_db(Splitter._extract_fit, Splitter._extract_eval)
        for data, fname in zip(
            [self._fit, self._eval],
            [fit_fname, eval_fname],
        ):
            DataFrame(data).to_csv(fname, index=False)

    def _scan_db(
        self,
        /,
        pre_action: Callable[[Splitter, Series], None] = None,
        post_action: Callable[[Splitter, Series], None] = None,
        *,
        pre_kwargs: dict = {},
        post_kwargs: dict = {},
    ):
        """Iterate through database. Perform pre/post actions on each article

        Parameters
        ----------
        pre_action: Callable(self, Series) -> None
            call this function on each article that is :code:`< cutoff_date`
        post_action: Callable(self, Series) -> None
            call this function on each article that is :code:`>= cutoff_date`
        pre_kwargs: Any
            passed to :code:`pre_action`
        post_kwargs: Any
            passed to :code:`post_action`
        """
        for articles in read_csv(
                self._dbase_fname,
                chunksize=self._chunk_size,
        ):

            # iterate through articles in chunk
            for _, article in articles.iterrows():

                # check article date
                article_date = DBaseBuilder._get_date(
                    article[self._date_field]
                )

                # check which action to perform
                do_pre = (
                    pre_action is not None
                    and article_date < self._cutoff_date
                )
                do_post = (
                    post_action is not None
                    and article_date >= self._cutoff_date
                )

                # perform pre/post actions
                if do_pre:
                    pre_action(self, article, **pre_kwargs)
                elif do_post:
                    post_action(self, article, **post_kwargs)

    def _count(self, article: Series, /):
        """Count total/positive articles

        :code:`pre_action` for :meth:`_scan_db`

        :code:`self._total` and :code:`self._num_pos` must be initialized
        before using this function

        Parameters
        ----------
        article: Series
            current article
        """
        self._total += 1
        self._num_pos += article['label']

    def _extract_fit(self, article: Series, /):
        """Extract article for fitting

        :code:`self._fit` must be initialized before using this function

        Parameters
        ----------
        article: Series
            current article
        """
        if article['label'] or random() < self._prob_incl:
            self._fit.append(article)

    def _extract_eval(self, article: Series, /):
        """Extract article for evaluation

        :code:`self._eval` must be initialized before using this function

        Parameters
        ----------
        article: Series
            current article
        """
        self._eval.append(article)


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
