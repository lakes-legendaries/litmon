"""use ml model to score documents"""

from argparse import ArgumentParser

import numpy
from pandas import read_csv
from sklearn.svm import LinearSVR
import yaml


class Modeler:
    """Use ML to score documents

    Parameters
    ----------
    fit_csv_fname: str
        Input filename for csv training data
    fit_npy_fname: str
        Input filename for vectorized training data
    eval_npy_fname: str
        Input filename for vectorized testing data
    eval_score_fname: str
        Output file name for testing data scores
    **kwargs: Any
        Passed to :code:`sklearn.svm.LinearSVR`

    Attributes
    ----------
    model: sklearn.svm.LinearSVR
        trained model
    """
    def __init__(
        self,
        /,
        fit_csv_fname: str,
        fit_npy_fname: str,
        eval_npy_fname: str,
        eval_scores_fname: str,
        **kwargs
    ):

        # load data
        fit_y = read_csv(fit_csv_fname)['label'].to_numpy()
        fit_x = numpy.load(fit_npy_fname)
        eval_x = numpy.load(eval_npy_fname)

        # train model
        self.model = LinearSVR(**kwargs).fit(fit_x, fit_y)

        # score eval articles
        eval_scores = self.model.predict(eval_x)

        # write to file
        numpy.save(eval_scores_fname, eval_scores)


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

    # create database
    Modeler(
        fit_csv_fname=config['fname']['fit_csv'],
        fit_npy_fname=config['fname']['vec_fit'],
        eval_npy_fname=config['fname']['vec_eval'],
        eval_scores_fname=config['fname']['eval_scores'],
        **config['kwargs']['model'],
    )
