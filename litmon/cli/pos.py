"""Build database of positive (target) articles"""

from pandas import DataFrame

from litmon.utils.cli import cli
from litmon.query import PubMedQuerier


class PositiveQuerier(PubMedQuerier):
    """Build database of positive (target) articles from given pmids

    Parameters
    ----------
    pmids_fname: str, optional, default='data/pmids.txt'
        List of pmids from target articles
    pos_fname: str, optional, default='data/positive_articles.csv'
        name of output file for positive articles
    batch_size: int, optional, default=100
        Nummber of pmids to query at once
    **kwargs: Any
        Passed to base class :class:`~litmon.query.PubMedQuerier`.
    """
    def __init__(
        self,
        /,
        pmids_fname: str = 'data/pmids.txt',
        pos_fname: str = 'data/positive_articles.csv',
        *,
        batch_size: int = 100,
        **kwargs
    ):

        # load in pmids
        pmids = open(pmids_fname).read().splitlines()

        # initialize base
        PubMedQuerier.__init__(self, **kwargs)

        # Initialize df of resulting articles
        pos_articles = DataFrame([], columns=self.header)

        # run query in batches
        for batch_start in range(0, len(pmids), batch_size):

            # get meta-data
            batch_end = min(batch_start + batch_size, len(pmids))

            # create query
            query = ''
            for id in pmids[batch_start: batch_end]:
                if len(query) > 0:
                    query += ' OR '
                query += f'({id} [PMID])'

            # run query
            queried_articles = self.query(query)

            # save results
            pos_articles = pos_articles.append(queried_articles)

        # save to file
        pos_articles.to_csv(pos_fname, index=False)


# command-line interface
if __name__ == '__main__':
    config = cli(
        cls='litmon.cli.pos.PositiveQuerier',
        description='Build dabase of positive (target) articles',
        default=['user'],
    )
    PositiveQuerier(**config)
