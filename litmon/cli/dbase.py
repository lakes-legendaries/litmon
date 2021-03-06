"""Build database of articles"""

from __future__ import annotations

from copy import deepcopy
from datetime import date, timedelta
from random import random, seed

from ezazure import Azure
from pandas import DataFrame

from litmon.query import PubMedQuerier
from litmon.utils import cli, drange


class DBaseBuilder(PubMedQuerier):
    """Build database of articles for each month

    Parameters
    ----------
    query: str
        standard pubmed query for pulling these types of articles
    date_range: str
        months to query. Format: YYYY/mm-YYYY/mm
    balance_ratio: float, optional, default=3
        number negative (non-target) articles = number positive (target)
        articles * :code:`balance_ratio`. To turn off, set to 0.
    dbase_dir: str, optional, default='data'
        directory to output database files to.
        :code:`dbase_fname=f'{dbase_dir}/{year}-{month:02d}{dbase_suffix}.csv'`
    dbase_suffix: str, optional, default=''
        suffix appended to each output file. See :code:`dbase_dir`
    pmids_fname: str, optional, default='data/pmids.txt'
        file containing positive (target) pmids. This is used for labeling
        documents True/False.
    random_seed: int, optional, default=271828
        random seed for :code:`random.seed()`. Set to 0 to turn off
    verbose: bool, optional, default=True
        write running status to console
    **kwargs: Any
        Passed to base class :class:`~litmon.query.PubMedQuerier`.
    """
    def __init__(
        self,
        /,
        query: str,
        date_range: str,
        *,
        balance_ratio: float = 3,
        dbase_dir: str = 'data',
        dbase_suffix: str = '',
        pmids_fname: str = 'data/pmids.txt',
        random_seed: int = 271828,
        verbose: bool = True,
        **kwargs
    ):

        # set seed
        if random_seed >= 0:
            seed(random_seed)

        # initialize base
        PubMedQuerier.__init__(self, **kwargs)

        # load positive pmids
        Azure().download(pmids_fname)
        pmids = open(pmids_fname).read().splitlines()

        # get file header
        file_header = deepcopy(self.header)
        file_header.append('label')

        # build database for each month
        for year, month in drange(date_range):

            # initialize df
            articles = DataFrame([], columns=file_header)

            # run query for each date
            qdate = date(year, month, 1)
            while qdate.month == month:

                # create query
                datestr = qdate.strftime('%Y/%m/%d')
                cur_query = f'{query} AND ({datestr} [edat])'

                # run query
                qarticles = self.query(cur_query)

                # remove articles with bad dates
                drop_idx = []
                for idx, article in qarticles.iterrows():
                    if not (
                        type(article['publication_date']) is date
                        and article['publication_date'] == qdate
                    ):
                        drop_idx.append(idx)
                qarticles.drop(index=drop_idx, inplace=True)

                # append to df
                articles = articles.append(qarticles)

                # increment day
                qdate += timedelta(days=1)

            # reset indices
            articles.reset_index(drop=True, inplace=True)

            # label articles positive / negative
            for _, article in articles.iterrows():
                cur_pmid = article['pubmed_id']
                cur_pmid = cur_pmid[0:min(len(cur_pmid), 8)]
                article['label'] = any([
                    cur_pmid == pmid
                    for pmid in pmids
                ])

            # balance df
            if balance_ratio > 0:
                prob_incl = (
                    balance_ratio
                    * articles['label'].sum()
                    / articles.shape[0]
                )
                drop_idx = []
                for idx, article in articles.iterrows():
                    if not article['label'] and random() > prob_incl:
                        drop_idx.append(idx)
                articles.drop(index=drop_idx, inplace=True)

            # write to file
            articles.to_csv(
                f'{dbase_dir}/{year:4d}-{month:02d}{dbase_suffix}.csv')

            # write running status
            if verbose:
                print(
                    f'{year:4d}-{month:02d}: '
                    f'{articles.shape[0]:4d} Articles '
                    f'| {articles["label"].sum():3d} Positive'
                )


# command-line interface
if __name__ == '__main__':
    config = cli(
        cls='litmon.cli.dbase.DBaseBuilder',
        description='Build database of articles',
        default=['query', 'user', 'fit_dates', 'dbase_fit'],
    )
    DBaseBuilder(**config)
