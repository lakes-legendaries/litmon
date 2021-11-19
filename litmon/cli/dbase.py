"""Build database of articles"""

from copy import deepcopy
from datetime import date, timedelta
from random import random
import re

from pandas import DataFrame

from litmon.query import PubMedQuerier
from litmon.utils.cli import cli
from litmon.utils.cloud import Azure


class DBaseBuilder(PubMedQuerier):
    """Build database of articles

    Parameters
    ----------
    query: str
        standard pubmed query for pulling these types of articles
    first_month: str
        first month to query. Format: YYYY/mm
    final_month: str
        final month to query. Format: YYYY/mm
    balance_ratio: float, optional, default=5
        number negative (non-target) articles = number positive (target)
        articles * :code:`balance_ratio`. To turn off, set to 0.
    suffix: str, optional, default=''
        suffix appended to each output file.
        :code:`output_fname=f'{year}-{month}{suffix}.csv'`
    pmids_fname: str, optional, default='data/pmids.txt'
        file containing positive (target) pmids. This is used for labeling
        documents True/False.
    **kwargs: Any
        Passed to base class :class:`~litmon.query.PubMedQuerier`.
    """
    def __init__(
        self,
        /,
        query: str,
        first_month: str,
        final_month: str,
        *,
        balance_ratio: float = 5,
        suffix: str = '',
        pmids_fname: str = 'data/pmids.txt',
        **kwargs
    ):

        # initialize base
        PubMedQuerier.__init__(self, **kwargs)

        # load positive pmids
        Azure.download(pmids_fname, private=True)
        pmids = open(pmids_fname).read().splitlines()

        # parse date arguments
        first_year, first_month = \
            (int(x) for x in re.findall(r'\d+', first_month))
        final_year, final_month = \
            (int(x) for x in re.findall(r'\d+', final_month))

        # get file header
        file_header = deepcopy(self.header)
        file_header.append('label')

        # build database for each month
        (year, month) = (first_year, first_month)
        while (year, month) <= (final_year, final_month):

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
            articles.to_csv(f'data/{year}-{month}{suffix}.csv')

            # increment month
            if month < 12:
                month += 1
            else:
                month = 1
                year += 1


# command-line interface
if __name__ == '__main__':
    config = cli(
        cls='litmon.cli.dbase.DBaseBuilder',
        description='Build database of articles',
        default=['query', 'user', 'dbase_fit'],
    )
    DBaseBuilder(**config)
