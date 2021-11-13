"""use ml model to score documents"""

from __future__ import annotations

import pickle
from random import random
from typing import Any

from nptyping import NDArray
from numpy import array
from pandas import DataFrame, read_csv
from sklearn.svm import LinearSVR
from vhash import VHash


class ArticleScorer:
    """Score journal articles based on their similarity to a training set

    This class vectorizes labeled (True/False, i.e. target/non-target) journal
    articles with :code:`vhash.VHash`, and then predicts scores with
    :code:`sklearn.svm.LinearSVR`.

    This class is designed to work with large datasets that cannot be loaded
    into memory all at once. During training, it iterates through a largely
    unbalanced dataset and extracts a much smaller balanced fitting set. During
    testing, it breaks the dataset into chunks and computes scores on each
    chunk individually.

    Parameters
    ----------
    balance_ratio: float, optional, default=3
        number negative (non-target) articles = number positive (target)
        articles * :code:`balance_ratio`
    chunk_size: int, optional, default=10E3
        number of articles to process from :code:`dbase_fname` at once
    max_iter: int, optional, default=1E6
        :code:`max_iter` for :code:`sklearn.svm.LinearSVR`
    ml_kwargs: dict, optional, default={}
        passed to :code:`sklearn.svm.LinearSVR` on :code:`__init__()`. do NOT
        include :code:`max_iter`
    use_cols: list[str], optional, default=None
        Article columns to use. If None, use:

        #. abstract
        #. authors
        #. conclusions
        #. journal
        #. keywords
        #. methods
        #. results
        #. title

    vhash_kwargs: dict, optional, default={}
        passed to :code:`vhash.VHash` on :code:`__init__()`

    Attributes
    ----------
    model: sklearn.svm.LinearSVR
        ml model for scoring
    vhash: vhash.VHash
        vectorizing hash table
    """
    def __init__(
        self,
        /,
        *,
        balance_ratio: float = 3,
        chunk_size: int = 10E3,
        max_iter: int = 1E6,
        ml_kwargs: dict = {},
        use_cols: list[str] = None,
        vhash_kwargs: dict = {},
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

        # save parameters
        self._balance_ratio = balance_ratio
        self._chunk_size = chunk_size
        self._max_iter = max_iter
        self._ml_kwargs = ml_kwargs
        self._use_cols = use_cols
        self._vhash_kwargs = vhash_kwargs

    def fit(self, dbase_fname: str, /) -> ArticleScorer:
        """Fit model

        Parameters
        ----------
        dbase_fname: str
            Name of database to use for fitting

        Returns
        -------
        ArticleScorer
            Calling instance
        """

        # get article count
        num_pos = 0
        total = 0
        for articles in read_csv(dbase_fname, chunksize=self._chunk_size):
            total += articles.shape[0]
            for _, article in articles.iterrows():
                num_pos += article['label']

        # get selection probability
        prob_incl = self._balance_ratio * num_pos / total

        # create dataset
        fit_set = []
        for articles in read_csv(dbase_fname, chunksize=self._chunk_size):
            for _, article in articles.iterrows():
                if article['label'] or random() < prob_incl:
                    fit_set.append(article)
        fit_set = DataFrame(fit_set)

        # get fitting text and labels
        text = self._extract_text(fit_set)
        labels = list(fit_set['label'].to_numpy())

        # train vectorizer
        self.vhash = VHash(**self._vhash_kwargs).fit(text, labels)

        # vectorize documents
        vectorized = self.vhash.transform(text)

        # train ml model
        self.model = LinearSVR(
            max_iter=self._max_iter,
            **self._ml_kwargs,
        ).fit(vectorized, labels)

        # return
        return self

    def fit_predict(self, dbase_fname: str, /) -> NDArray[(Any,), float]:
        """Fit model, predict scores

        Parameters
        ----------
        dbase_fname: str
            Name of database to use for fitting

        Returns
        -------
        NDArray
            Score for each article in :code:`dbase_fname`
        """
        return self.fit(dbase_fname).predict(dbase_fname)

    def predict(self, dbase_fname: str, /) -> NDArray[(Any,), float]:
        """Predict scores for each article in :code:`dbase_fname`

        Parameters
        ----------
        dbase_fname: str
            Name of database to use for fitting

        Returns
        -------
        NDArray
            Score for each article in :code:`dbase_fname`
        """
        pred = []
        for articles in read_csv(dbase_fname, chunksize=self._chunk_size):
            text = self._extract_text(articles)
            vectorized = self.vhash.transform(text)
            pred.extend(self.model.predict(vectorized))
        return array(pred)

    def save(self, fname: str, /):
        """Save instance to file

        This is necessary because :code:`vhash.VHash` is not picklable.

        This will actually save two files: :code:`fname.bin` and
        :code:`fname.pickle`. Both are required when using :meth:`load`.

        Parameters
        ----------
        fname: str
            Output file, without file extension
        """
        self.vhash.save(f'{fname}.bin')
        self.vhash = None
        pickle.dump(self, open(f'{fname}.pickle', 'wb'))
        self.vhash = VHash.load(f'{fname}.bin')

    @classmethod
    def load(cls, fname: str, /) -> ArticleScorer:
        """Load instance from file

        Fname should be a file root without extension (same as the argument you
        passed to :meth:`save`). This will load data from :code:`fname.bin` and
        :code:`fname.pickle`.

        Parameters
        ----------
        fname: str
            Input file, without file extension

        Returns
        -------
        ArticleScorer
            loaded instance
        """
        out = pickle.load(open(f'{fname}.pickle', 'rb'))
        out.vhash = VHash.load(f'{fname}.bin')
        return out

    def _extract_text(self, df: DataFrame) -> list[str]:
        """Extract text columns from a dataframe

        Parameters
        ----------
        df: DataFrame
            data to process

        Returns
        -------
        list[str]
            extracted text with :code:`self._use_cols` concatenated
        """
        return [
            ' '.join(
                [
                    str(row[field])
                    for field in self._use_cols
                ]
            )
            for _, row in df.iterrows()
        ]
