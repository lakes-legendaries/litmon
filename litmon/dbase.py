"""Build database of articles"""

from argparse import ArgumentParser
from copy import deepcopy
from datetime import date, datetime, timedelta
from logging import basicConfig, info, INFO
from typing import Any

from nptyping import NDArray
from numpy import arange, array, zeros
from pandas import DataFrame, read_csv, Series
import yaml

from litmon.query import PubMedQuerier


class DBaseBuilder(PubMedQuerier):
    """Build database of articles

    Parameters
    ----------
    dbase_fname: str
        name of output file
    pos_fname: str
        name of positive (target) articles file
    query: str
        standard pubmed query for pulling these types of articles
    log_fname: str, optional, default=logs/dbase.log
        file to log progress to
    min_date: str, optional, default=None
        minimum date to query, in format YYYY/MM/DD
    max_date: str, optional, default=None
        maximum date to query, in format YYYY/MM/DD
    **kwargs: Any
        Passed to base class :class:`~litmon.query.PubMedQuerier`.
    """
    def __init__(
        self,
        /,
        dbase_fname: str,
        pos_fname: str,
        query: str,
        *,
        log_fname: str = 'logs/dbase.log',
        min_date: str = None,
        max_date: str = None,
        **kwargs
    ):

        # load positive articles
        pos_articles = read_csv(pos_fname)

        # initialize base
        PubMedQuerier.__init__(self, **kwargs)

        # setup logger
        if log_fname is not None:

            # clear out existing file
            with open(log_fname, 'w'):
                pass

            # set basic logging parameters
            basicConfig(
                filename=log_fname,
                level=INFO,
            )

        # parse date arguments
        if min_date is not None:
            min_date = datetime.strptime(min_date, '%Y/%m/%d').date()
        if max_date is not None:
            max_date = datetime.strptime(max_date, '%Y/%m/%d').date()

        # extract dates from positive articles
        dates = self.__class__._get_dates(pos_articles['publication_date'])

        # get date bounds
        min_date: date = (
            min(dates)
            if min_date is None
            else max(min_date, min(dates))
        )
        max_date: date = (
            max(dates)
            if max_date is None
            else min(max_date, max(dates))
        )

        # write file header
        file_header = deepcopy(self.header)
        file_header.insert(0, 'index')
        file_header.append('label')
        DataFrame([], columns=file_header).to_csv(dbase_fname, index=False)

        # run queries
        count = 0
        cur_date = min_date
        while cur_date <= max_date:

            # create query
            datestr = cur_date.strftime('%Y/%m/%d')
            cur_query = f'{query} AND ({datestr} [edat])'

            # run query
            articles = self.query(cur_query)

            # remove articles with bad dates
            keep_me = zeros(articles.shape[0], dtype=bool)
            for n, (_, article) in enumerate(articles.iterrows()):
                keep_me[n] = (
                    type(article['publication_date']) is date
                    and article['publication_date'] == cur_date
                )
            articles = articles.iloc[keep_me, :].reset_index()

            # label articles positive / negative
            articles['label'] = 0
            for n, (_, article) in enumerate(articles.iterrows()):
                articles.loc[n, 'label'] = any([
                    article['pubmed_id'] == pos_pmid
                    for pos_pmid in pos_articles['pubmed_id']
                ])

            # increment index
            articles['index'] = arange(articles.shape[0]) + count
            count += articles.shape[0]

            # append to file
            articles.to_csv(
                dbase_fname,
                header=False,
                index=False,
                mode='a',
            )

            # log status
            if log_fname is not None:
                info(
                    f'{datestr}: {articles.shape[0]:4g} Articles '
                    f'/ {articles["label"].sum():2g} Positive'
                )

            # increment date
            cur_date += timedelta(days=1)

    @classmethod
    def _get_date(cls, datestr: str) -> date:
        """Convert datestr to date

        Parameters
        ----------
        datestr: str
            date as str, in formt YYYY-mm-dd

        Returns
        -------
        date
            formatted date, or None if is ill-formatted
        """
        try:
            return datetime.strptime(datestr, '%Y-%m-%d').date()
        except Exception:
            try:
                return datetime.strptime(datestr, '%Y/%m/%d').date()
            except Exception:
                return None

    @classmethod
    def _get_dates(cls, datestr: Series) -> NDArray[(Any,), date]:
        """Extract dates from a Series

        Parameters
        ----------
        datestr: Series of str
            dates, in format YYYY-mm-dd.
            Any ill-formed dates will be discarded

        Returns
        -------
        NDArray
            extracted dates
        """
        dates = [
            DBaseBuilder._get_date(d)
            for d in datestr
        ]
        return array([d for d in dates if d])


# command-line interface
if __name__ == '__main__':

    # parse command-line arguments
    parser = ArgumentParser('Build dabase of articles')
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

    # create database
    DBaseBuilder(
        dbase_fname=config['fname']['dbase'],
        pos_fname=config['fname']['pos'],
        query=config['query'],
        min_date=config['dates']['fit_start'],
        max_date=config['dates']['eval_end'],
        **config['user'],
        **config['kwargs']['query'],
        **config['kwargs']['dbase'],
    )
