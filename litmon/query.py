"""Base class for querying PubMed articles"""

from __future__ import annotations

from retry import retry
from pandas import DataFrame
from pymed import PubMed
from pymed.article import PubMedArticle


class PubMedQuerier:
    """Base class for querying PubMed articles

    Parameters
    ----------
    email: str
        email of the user of this program.
        this is required by the PubMed api
    tool: str
        name of the program running this query.
        this is required by the PubMed api
    max_results: int, optional, default=1000
        Maximum number of PubMed articles retrieved in any single query.
        Required by the :code:`pymed.PubMed` tool

    Attributes
    ----------
    count: int
        total number of articles queried by this instance
    header: list[str]
        name of each field pulled from pubmed
    """
    def __init__(
        self,
        /,
        email: str,
        tool: str,
        *,
        max_results: int = 1000,
    ):
        # initialize tool
        self._pubmed = PubMed(
            tool=tool,
            email=email,
        )

        # get file header
        self.header = [
            field
            for field in dir(PubMedArticle)
            if not callable(getattr(PubMedArticle, field))
            and field[0] != '_'
        ]

        # save parameters
        self._max_results = max_results

        # initialize count of articles
        self.count = 0

    @retry(delay=3)
    def query(self, query: str, /) -> DataFrame:
        """Query PubMed servers

        This function is encased in an infinite retry loop, which is necessary
        due to frequent connection interruptions or failures to properly
        download data.

        Parameters
        ----------
        query: str
            query to send to PubMed servers

        Returns
        -------
        DataFrame
            resulting articles
        """

        # query pubmed
        articles_it = self._pubmed.query(
            query,
            max_results=self._max_results,
        )

        # convert to df
        articles_df = DataFrame(
            [
                [
                    getattr(article, field)
                    if hasattr(article, field)
                    else ''
                    for field in self.header
                ]
                for article in articles_it
            ],
            columns=self.header,
        )

        # ensure that each row in resulting database has a unique index
        articles_df.index += self.count
        self.count += articles_df.shape[0]

        # return
        return articles_df
