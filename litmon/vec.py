"""Vectorize datasets"""

from argparse import ArgumentParser

import numpy
from pandas import DataFrame, read_csv
from vhash import VHash
import yaml


class Vectorizer:
    """Vectorize datasets

    Parameters
    ----------
    fit_csv_fname: str
        Input fitting filename (csv)
    fit_npy_fname: str
        Output fitting filename (bin)
    eval_csv_fname: str
        Input evaluation filename (csv)
    eval_npy_fname: str
        Output evaluation filename (bin)
    chunk_size: int, optional, default=10e3
        number of articles to process from :code:`eval_csv_fname` at once
    use_cols: list[str], optional, default=None
        Article columns to use.
        If None, use:

        #. abstract
        #. authors
        #. conclusions
        #. journal
        #. keywords
        #. methods
        #. results
        #. title

    **kwargs: Any
        Used when constructing :code:`vhash.Vhash`

    Attributes
    ----------
    vhash: vhash.VHash
        trained vectorizer
    """
    def __init__(
        self,
        /,
        fit_csv_fname: str,
        fit_npy_fname: str,
        eval_csv_fname: str,
        eval_npy_fname: str,
        *,
        chunk_size: int = 10e3,
        use_cols: list[str] = None,
        **kwargs
    ):
        # get default parameters
        if use_cols is None:
            use_cols = [
                'abstract',
                'authors',
                'conclusions',
                'journal',
                'keywords',
                'methods',
                'results',
                'title',
            ]

        # load fitting data
        fit_csv = read_csv(fit_csv_fname)

        # extract text
        fit_txt = self.__class__._extract_text(fit_csv, use_cols)

        # train vectorizer
        fit_y = list(fit_csv['label'].to_numpy())
        self.vhash = VHash(**kwargs).fit(fit_txt, fit_y)

        # vectorize documents
        fit_npy = self.vhash.transform(fit_txt)

        # process eval set
        eval_npy = []
        for eval_csv in read_csv(eval_csv_fname, chunksize=chunk_size):

            # extract text
            eval_txt = self.__class__._extract_text(eval_csv, use_cols)

            # vectorize documents
            eval_npy.extend(self.vhash.transform(eval_txt))

        # save to file
        numpy.save(fit_npy_fname, fit_npy)
        numpy.save(eval_npy_fname, eval_npy)

    @classmethod
    def _extract_text(
        cls,
        df: DataFrame,
        use_cols: list[str]
    ) -> list[str]:
        """Extract text columns from a dataframe

        Parameters
        ----------
        df: DataFrame
            data to process
        use_cols: list[str]
            columns to extract

        Returns
        -------
        list[str]
            extracted text with :code:`use_cols` concatenated
        """
        return [
            ' '.join(
                [
                    str(row[field])
                    for field in use_cols
                ]
            )
            for _, row in df.iterrows()
        ]


# command-line interface
if __name__ == '__main__':

    # parse command-line arguments
    parser = ArgumentParser('Vectorize datasets')
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

    # vectorize documents
    Vectorizer(
        fit_csv_fname=config['fname']['fit_csv'],
        fit_npy_fname=config['fname']['fit_npy'],
        eval_csv_fname=config['fname']['eval_csv'],
        eval_npy_fname=config['fname']['eval_npy'],
        **config['kwargs']['vec'],
    )
