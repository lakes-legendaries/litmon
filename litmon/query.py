"""Base class for querying PubMed articles"""

from __future__ import annotations

from datetime import date
from typing import Any

from nptyping import NDArray
from numpy import array, NaN
from retry import retry
from pandas import DataFrame
from pymed import PubMed
from pymed.article import PubMedArticle


class PubMedQuerier:
    """Base class for querying PubMed articles

    This class is designed for building large datasets: After each query, the
    resulting articles are appended to file.

    Parameters
    ----------
    fname: str, optional
        name of output file.
        If None, then don't append results to file
    email: str, optional, default='mike@lakeslegendaries.com'
        email of the user of this program.
        this is required by the PubMed api
    max_results: int, optional, default=1000
        Maximum number of PubMed articles retrieved in any single query.
        Required by the :code:`pymed.PubMed` tool
    tool: str, optional, default='org.mfoundation.litmon'
        name of the program running this query.
        this is required by the PubMed api
    """
    def __init__(
        self,
        /,
        fname: str = None,
        *,
        email: str = 'mike@lakeslegendaries.com',
        max_results: int = 1000,
        tool: str = 'org.mfoundation.litmon',
    ):
        # initialize tool
        self._pubmed = PubMed(
            tool=tool,
            email=email,
        )

        # get file header
        self._header = [
            field
            for field in dir(PubMedArticle)
            if not callable(getattr(PubMedArticle, field))
            and field[0] != '_'
        ]

        # write file header
        if fname is not None:
            DataFrame([], columns=self._header).to_csv(fname)

        # save parameters
        self._fname = fname
        self._max_results = max_results

        # initialize count of articles
        self._count = 0

    @retry(delay=3)
    def query(
        self,
        query: str,
        /,
    ) -> tuple(DataFrame, NDArray[(Any,), date]):
        """Query PubMed servers, append results to file

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
        NDArray of shape(num_articles,) of type :code:`date`
            date of each resulting article
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
                    for field in self._header
                ]
                for article in articles_it
            ],
            columns=self._header,
        )

        # ensure that each row in resulting database has a unique index
        articles_df.index += self._count
        self._count += articles_df.shape[0]

        # append articles to file
        if self._fname is not None:
            articles_df.to_csv(
                self._fname,
                header=False,
                mode='a',
            )

        # get dates of articles
        dates = articles_df['publication_date']
        dates = array([
            d if isinstance(d, date) else NaN
            for d in dates
        ])

        # return
        return articles_df, dates
