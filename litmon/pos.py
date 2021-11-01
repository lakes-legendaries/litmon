"""Build database of positive (target) articles"""

from argparse import ArgumentParser
from typing import Any

from nptyping import NDArray
import yaml

from litmon.query import PubMedQuerier


class PositiveQuerier(PubMedQuerier):
    """Build database of positive (target) articles from given pmids

    Parameters
    ----------
    fname: str
        name of output file
    pmids: NDArray of shape(num_articles,) of type str
        List of pmids from target articles
    batch_size: int, optional, default=100
        Nummber of pmids to query at once
    **kwargs: Any
        Passed to base class :class:`~litmon.query.PubMedQuerier`.
    """
    def __init__(
        self,
        /,
        fname: str,
        pmids: NDArray[(Any,), str],
        *,
        batch_size: int = 100,
        **kwargs
    ):

        # initialize base
        PubMedQuerier.__init__(
            self,
            fname=fname,
            **kwargs
        )

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

            # run query, appending result to file
            self.query(query)


# command-line interface
if __name__ == '__main__':

    # parse command-line arguments
    parser = ArgumentParser('Build dabase of positive (target) articles')
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

    # load pmids
    pmids = open(config['fname']['pmids']).read().splitlines()

    # create database
    PositiveQuerier(
        fname=config['fname']['pos'],
        pmids=pmids,
        **config['kwargs']['pos']
    )
