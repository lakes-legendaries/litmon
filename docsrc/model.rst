.. _model:

#############################
Identifying Relevant Articles
#############################

Once you have a training dataset, you can build up a model that differentiates
between relevant (target/positive) and irrelevant (non-target/negative)
articles. This is done with the :class:`litmon.model.ArticleScorer` class.

This model vectorizes text documents using the `vhash
<https://lakes-legendaries.github.io/vhash/>`_ package. Then, this model uses a
machine learning (ML) model to find the articles most relevant to aging
research. The default ML model is :code:`sklearn.svm.LinearSVR`, but you can
specify any import-able machine learning model that is compliant to the sklearn
api.

******************
Training the Model
******************

To train the article-scoring model, run:

.. code-block:: bash

   python litmon/cli/fit.py

This constructs :class:`litmon.cli.fit.ModelFitter`, using the
:code:`fit_dates` and :code:`fit` fields from :code:`config/std.yaml`, and
outputs the trained model to :code:`data/model.bin` and
:code:`data/model.pickle` (if you are using the standard configuration). Both
of these files are required for the model to be loaded back in.

********************
Identifying Articles
********************

To use a previously-trained article-scoring model to score new articles, run:

.. code-block:: bash

   python litmon/cli/eval.py

This constructs :class:`litmon.cli.eval.ModelUser`, using the
:code:`eval_dates` field from :code:`config/std.yaml`, and outputs the most
relevant articles to :code:`data/*-results.xlsx`, where there is one
:code:`data/*-results.xlsx` file for each :code:`data/*-eval.csv` dataset.

The number of articles written can be customized in the :code:`config/std.yaml`
file by adding :code:`eval: {count: 100}` to :code:`config/std.yaml`
and calling the above script with the :code:`-f eval_dates eval` flag.

*************
API Reference
*************

ArticleScorer
-------------

.. autoclass:: litmon.model.ArticleScorer
   :members: fit, fit_predict, predict, save, load

ModelFitter
-----------

.. autoclass:: litmon.cli.fit.ModelFitter

ModelUser
---------

.. autoclass:: litmon.cli.eval.ModelUser
