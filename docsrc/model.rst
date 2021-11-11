################################
Build ML Model to Score Articles
################################

Once all articles have been vectorized, we build machine learning models to
find the articles most relevant to aging research.

The training set is used to train a :code:`sklearn.svm.LinearSVR` model. All
articles in the evaluating set are then scored, and results are written to
file.

*************
API Reference
*************

.. autoclass:: litmon.model.Modeler
