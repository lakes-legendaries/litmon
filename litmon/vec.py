"""Vectorize datasets"""

from argparse import ArgumentParser

import numpy
from numpy import array
from pandas import read_csv
from vhash import VHash
import yaml


class Vectorizer:
    """Vectorize datasets

    Parameters
    ----------
    fit_ifname: str
        Input fitting filename (csv)
    fit_ofname: str
        Output fitting filename (bin)
    eval_ifname: str
        Input evaluation filename (csv)
    eval_ofname: str
        Output evaluation filename (bin)
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
        fit_ifname: str,
        fit_ofname: str,
        eval_ifname: str,
        eval_ofname: str,
        *,
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

        # load files
        fit_set = read_csv(fit_ifname)
        eval_set = read_csv(eval_ifname)

        # convert df -> list[str] by concatenating columns
        text = [
            [
                ' '.join(
                    [
                        str(row[field])
                        for field in use_cols
                    ]
                )
                for _, row in set.iterrows()
            ]
            for set in [fit_set, eval_set]
        ]

        # get labels
        labels = [
            list(set['label'].to_numpy())
            for set in [fit_set, eval_set]
        ]

        # train vectorizer
        self.vhash = VHash(**kwargs).fit(text[0], labels[0])

        # vectorize text
        vec = [
            array(self.vhash.transform(t))
            for t in text
        ]

        # write results to file
        numpy.save(fit_ofname, vec[0])
        numpy.save(eval_ofname, vec[1])


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

    # load pmids
    pmids = open(config['fname']['pmids']).read().splitlines()

    # create database
    Vectorizer(
        fit_ifname=config['fname']['fit'],
        fit_ofname=config['fname']['vec_fit'],
        eval_ifname=config['fname']['eval'],
        eval_ofname=config['fname']['vec_eval'],
        **config['kwargs']['vec'],
    )
