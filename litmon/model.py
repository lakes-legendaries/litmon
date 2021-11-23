"""use ml model to score documents"""

from __future__ import annotations

from importlib import import_module
import pickle
from typing import Any

from nptyping import NDArray
from numpy import array
from pandas import DataFrame
from vhash import VHash


class ArticleScorer:
    """Score journal articles based on their similarity to a training set

    This class vectorizes labeled (True/False, i.e. target/non-target) journal
    articles with :code:`vhash.VHash`, and then predicts scores with a machine
    learning model (default :code:`sklearn.svm.LinearSVR`).

    Parameters
    ----------
    label_field: str, optional, default='label'
        name of label field in dataframe used for fitting
    ml_model: str, optional, default='sklearn.svm.LinearSVR'
        name of machine learning model to use. You can specify any machine
        learning model that is installed in your local environment, as long as
        it is compliant to the sklearn api.
    ml_kwargs: dict, optional, default={}
        passed to :code:`ml_model` on :code:`__init__()`
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
    model: Type[ml_model]
        ml model for scoring
    vhash: vhash.VHash
        vectorizing hash table
    """
    def __init__(
        self,
        /,
        *,
        label_field: str = 'label',
        ml_model: str = 'sklearn.svm.LinearSVR',
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
        self._label_field = label_field
        self._ml_model = ml_model
        self._ml_kwargs = ml_kwargs
        self._use_cols = use_cols
        self._vhash_kwargs = vhash_kwargs

    def fit(self, X: DataFrame, /) -> ArticleScorer:
        """Fit model

        Parameters
        ----------
        X: DataFrame
            data to use for fitting

        Returns
        -------
        ArticleScorer
            Calling instance
        """

        # import ml class
        ml_module, ml_class = self._ml_model.rsplit('.', maxsplit=1)
        ml_class = getattr(import_module(ml_module), ml_class)

        # get fitting text and labels
        text = self._extract_text(X)
        labels = list(X[self._label_field].to_numpy())

        # train vectorizer
        self.vhash = VHash(**self._vhash_kwargs).fit(text, labels)

        # vectorize documents
        vectorized = self.vhash.transform(text)

        # train ml model
        self.model = ml_class(**self._ml_kwargs).fit(vectorized, labels)

        # return
        return self

    def fit_predict(self, X: DataFrame, /) -> NDArray[(Any,), float]:
        """Fit model, predict scores

        Parameters
        ----------
        X: DataFrame
            data to use for fitting and scoring

        Returns
        -------
        NDArray
            Score for each article in :code:`X`
        """
        return self.fit(X).predict(X)

    def predict(self, X: DataFrame, /) -> NDArray[(Any,), float]:
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
        text = self._extract_text(X)
        vectorized = self.vhash.transform(text)
        return array(self.model.predict(vectorized))

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
        X = self.vhash
        self.vhash = None
        pickle.dump(self, open(f'{fname}.pickle', 'wb'))
        self.vhash = X
        # self.vhash = VHash.load(f'{fname}.bin')

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
