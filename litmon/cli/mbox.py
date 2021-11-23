"""Extract PubMed IDs from mbox email dumps"""

from __future__ import annotations

import re
from typing import Any

from nptyping import NDArray
from numpy import unique

from litmon.utils import Azure, cli


class PubMedIDExtractor:
    """Extract PubMed IDs from mbox email dumps

    Parameters
    ----------
    mbox_fname: list[str]
        input mbox files
    pmids_fname: str, optional, default='data/pmids.txt'
        output file, containing target article pubmed ids
    pattern: str, optional, default='PMID.{0,1}[ ]*([0-9]{8})'
        regular expression to find PubMed IDs
    """

    def __init__(
        self,
        /,
        mbox_fname: list[str],
        pmids_fname: str = 'data/pmids.txt',
        *,
        pattern: str = 'PMID.{0,1}[ ]*([0-9]{8})',  # noqa
    ):

        # load mboxes
        mbox = []
        for fname in mbox_fname:
            Azure.download(fname, private=True)
            mbox.extend(open(fname, 'r').readlines())

        # get pmids
        ids: list[str] = []
        for line in mbox:
            for pmid in re.findall(pattern, line):
                ids.append(pmid)
        pmids: NDArray[(Any,), str] = unique(ids)

        # save to file
        with open(pmids_fname, 'w') as file:
            for line in pmids:
                print(line, file=file)


# command-line interface
if __name__ == '__main__':
    config = cli(
        cls='litmon.cli.mbox.PubMedIDExtractor',
        description='Extract PubMed IDs from mbox email dumps',
        default=['mbox_fname'],
    )
    extractor = PubMedIDExtractor(**config)
