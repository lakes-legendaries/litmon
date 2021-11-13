"""Build database of articles"""

from copy import deepcopy
from datetime import date, datetime, timedelta
from logging import basicConfig, info, INFO

from numpy import arange, zeros
from pandas import DataFrame

from litmon.query import PubMedQuerier
from litmon.utils.cli import cli


class DBaseBuilder(PubMedQuerier):
    """Build database of articles

    Parameters
    ----------
    query: str
        standard pubmed query for pulling these types of articles
    min_date: str
        first date to query, in format YYYY/MM/DD
    max_date: str
        last date to query, in format YYYY/MM/DD
    dbase_fname: str
        name of output file
    log_fname: str, optional, default=logs/dbase.log
        file to log progress to. If None, don't log
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
        min_date: str,
        max_date: str,
        dbase_fname: str,
        *,
        log_fname: str = None,
        pmids_fname: str = 'data/pmids.txt',
        **kwargs
    ):

        # initialize base
        PubMedQuerier.__init__(self, **kwargs)

        # load positive pmids
        pmids = open(pmids_fname).read().splitlines()

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
        min_date = datetime.strptime(min_date, '%Y/%m/%d').date()
        max_date = datetime.strptime(max_date, '%Y/%m/%d').date()

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
                cur_pmid = article['pubmed_id']
                cur_pmid = cur_pmid[0:min(len(cur_pmid), 8)]
                articles.loc[n, 'label'] = any([
                    cur_pmid == pmid
                    for pmid in pmids
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


# command-line interface
if __name__ == '__main__':
    config = cli(
        cls='litmon.cli.dbase.DBaseBuilder',
        description='Build database of articles',
        default=['query', 'user', 'dbase_fit'],
    )
    DBaseBuilder(**config)
