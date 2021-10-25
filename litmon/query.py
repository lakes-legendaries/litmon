from __future__ import annotations

from argparse import ArgumentParser
from datetime import datetime
from typing import Iterator

from retry import retry
from pandas import DataFrame
from pymed import PubMed
from pymed.article import PubMedArticle
import yaml


class PubMedInterface:
    """Easy interface to batch-query PubMed articles

    This class lets you build a large database of articles by running the same
    query for many different dates (e.g. all articles matching :code:`query`
    from 2011 through 2016).

    Parameters
    ----------
    fname: str
        fname of output file
    query: str
        pubmed query (excluding dates)
    start_date: str
        start date for query, in YYYY/MM/DD format.
        range of dates is :code:`[start_date, end_date)`
    end_date: str
        end date, in YYYY/MM/DD format.
        range of dates is :code:`[start_date, end_date)`
    email: str, optional, default='mike@lakeslegendaries.com'
        email of the user of this program.
        this is required by the pubmed api
    tool: str, optional, default='org.mfoundation.litmon'
        name of the program running this query.
        this is required by the pubmed api
    """
    def __init__(
        self,
        /,
        fname: str,
        query: str,
        start_date: str,
        end_date: str,
        *,
        email: str = 'mike@lakeslegendaries.com',
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

        # save other parameters
        self._fname = fname
        self._start_date = datetime.strptime(start_date, '%Y/%m/%d')
        self._end_date = datetime.strptime(end_date, '%Y/%m/%d')
        self._query = query

    def run_query(self):
        """Run PubMed query, saving results to file"""

        # clear output file
        with open(self._fname, 'w'):
            pass

        # write file header
        DataFrame([], columns=self._header).to_csv(self._fname, index=False)

        # run query for each date
        for year in range(self._start_date.year, self._end_date.year + 1):
            for month in range(1, 13):
                for day in range(1, 32):

                    # check if date is a valid day
                    try:
                        datestr = f'{year:4d}/{month:02d}/{day:02d}'
                        date = datetime.strptime(datestr, '%Y/%m/%d')
                    except ValueError:
                        continue

                    # check if date is in range
                    if date < self._start_date:
                        continue
                    if date >= self._end_date:
                        return

                    # run query for this date
                    articles = self._single_query(datestr)

                    # write articles to file
                    articles.to_csv(
                        self._fname,
                        header=False,
                        index=False,
                        mode='a',
                    )

    def _single_query(self, datestr: str, /, **kwargs) -> DataFrame:
        """Run query for a single date

        Parameters
        ----------
        datestr: str
            date to run query for.
            format: YYYY/MM/DD
        **kwargs: Any
            passed to _safe_query()

        Returns
        -------
        DataFrame
            articles matching query on :code:`datestr`
        """

        # get query for specific day
        query = f'{self._query} AND ({datestr} [edat])'

        # send query to pubmed servers
        results = self._safe_query(query, **kwargs)

        # format resulting articles
        articles = DataFrame(
            [
                [
                    getattr(result, field)
                    for field in self._header
                ]
                for result in results
            ],
            columns=self._header,
        )

        # set date
        articles['date'] = datestr

        # return df
        return articles

    @retry(delay=10)
    def _safe_query(
        self,
        query: str,
        /,
        *,
        max_results: int = 1000,
        **kwargs
    ) -> Iterator:
        """Safely send query to PubMed servers

        This function is encased in an infinite retry loop, which is necessary
        due to frequent connection interruptions or failures to properly
        download data.

        Parameters
        ----------
        query: str
            PubMed query
        max_results: int, optional, default=1000
            Maximum number of resulting articles
        **kwargs: Any, optional
            Additional kwargs to pass to PubMed.query()

        Returns
        -------
        Iterator
            articles found through query
        """
        return self._pubmed.query(
            query,
            max_results=max_results,
            **kwargs
        )


# command-line interface
if __name__ == '__main__':

    # parse arguments
    parser = ArgumentParser('Batch-query PubMed Articles')
    parser.add_argument(
        '-c',
        '--config_fname',
        default='config/query.yaml',
        help='Configuration yaml file. '
             'This file\'s variables are used to construct PubMedInterface()',
    )
    args = parser.parse_args()

    # load configuration
    config = yaml.safe_load(open(args.config_fname, 'r'))

    # run query
    PubMedInterface(**config).run_query()
