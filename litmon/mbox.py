"""Extract PubMed IDs from mbox email dumps"""

from __future__ import annotations

from argparse import ArgumentParser
import re
from typing import Any

from nptyping import NDArray
from numpy import unique
import yaml


class PubMedIDExtractor:
    """Extract PubMed IDs from mbox email dumps

    Parameters
    ----------
    data: list[str]
        file contents to parse
    pattern: str, optional, default='PMID.{0,1}[ ]*([0-9]{8})'
        regular expression to find PubMed IDs

    Attributes
    ----------
    pmids: NDArray of shape(num_articles,) of type str
        PubMed ids
    """  # noqa

    def __init__(
        self,
        data: list[str],
        /,
        *,
        pattern: str = 'PMID.{0,1}[ ]*([0-9]{8})',  # noqa
    ):

        # initialize attribute
        ids: list[str] = []

        # parse dadta
        for line in data:
            for pmid in re.findall(pattern, line):
                ids.append(pmid)

        # get unique
        self.pmids: NDArray[(Any,), str] = unique(ids)

    def to_file(self, fname: str, /):
        """Write PubMed ids to file

        Parameters
        ----------
        fname: str
            file to write to
        """
        with open(fname, 'w') as file:
            for line in self.pmids:
                print(line, file=file)


# command-line interface
if __name__ == '__main__':

    # parse command-line arguments
    parser = ArgumentParser('Extract PubMed IDs from mbox email dumps')
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

    # load mboxes
    mbox = []
    for fname in config['fname']['mbox']:
        mbox.extend(open(fname, 'r').readlines())

    # extract ids
    extractor = PubMedIDExtractor(mbox, **config['kwargs']['mbox'])

    # write results to file
    extractor.to_file(config['fname']['pmids'])
