"""Extract PubMed IDs from mbox email dumps"""

from __future__ import annotations

from argparse import ArgumentParser
import re

from numpy import unique


class PubMedIDExtractor:
    """Extract PubMed IDs from mbox email dumps

    Parameters
    ----------
    data: list[str]
        file contents to parse
    pattern: str, optional, default='PMID.{0,1}\s*([0-9]{8})'
        regular expression to find PubMed IDs

    Attributes
    ----------
    pmid: list[str]
        PubMed ids
    """  # noqa

    def __init__(
        self,
        data: list[str],
        /,
        *,
        pattern: str = 'PMID.{0,1}\s*([0-9]{8})',  # noqa
    ):

        # initialize attribute
        self.pmid: list[str] = []

        # parse dadta
        for line in data:
            for pmid in re.findall(pattern, line):
                self.pmid.append(pmid)

        # get unique
        self.pmid = list(unique(self.pmid))

    def to_file(self, fname: str, /):
        """Write PubMed ids to file

        Parameters
        ----------
        fname: str
            file to write to
        """
        with open(fname, 'w') as file:
            for line in self.pmid:
                print(line, file=file)


# command-line interface
if __name__ == '__main__':

    # parse command-line arguments
    parser = ArgumentParser('Extract PubMed IDs from mbox email dumps')
    parser.add_argument(
        '-i',
        '--ifname',
        help='Input filename (mbox file)',
    )
    parser.add_argument(
        '-o',
        '--ofname',
        help='Output filename (txt file containing pmids)',
    )
    args = parser.parse_args()

    # load mbox
    data = open(args.ifname, 'r').readlines()

    # extract ids
    extractor = PubMedIDExtractor(data)

    # write results to file
    extractor.to_file(args.ofname)
