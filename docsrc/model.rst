.. _model:

#############################
Identifying Relevant Articles
#############################

Once you have a training dataset, you can build up a model that differentiates
between relevant (target/positive) and irrelevant (non-target/negative)
articles. This is done with the :class:`litmon.model.ArticleScorer` class.

When you're training this class, the training set is downsampled. Articles are
included in the training set iff:

#. They are positive, or

#. If they are selected through the equation
   
   .. code-block:: python

      include_article = random() < num_positive / total * balance_ratio
   
   where:
   
      #. :code:`include_article` is whether an article is included

      #. :code:`random()` is a randomly-selected number from 0-1

      #. :code:`num_positive` is the total number of positive articles in
         the database before the cutoff date

      #. :code:`total` is the total number of articles in the database
         before the cutoff date

      #. :code:`balance_ratio` is an arbitrarily-chosen ratio (default=3)

This creates a set of articles that are reasonably-balanced data set for training.

Articles are then vectorized using the `vhash
<https://lakes-legendaries.github.io/vhash/>`_ package.

Once all fitting articles have been vectorized, we build and train a machine
learning model to find the articles most relevant to aging research. In this
package, We use a :code:`sklearn.svm.LinearSVR` model.

Finally, after training the ML model, all articles in the evaluation set can be
vectorized, and then scored via the ML model. The top-scoring models can then
be written to file as the final result of this pipeline.

******************
Training the Model
******************

To train the article-scoring model, run:

.. code-block:: bash

   python litmon/cli/fit.py

This constructs :class:`litmon.cli.fit.ModelFitter` (training on
:code:`data/dbase_fit.csv`), and outputs the trained model to
:code:`data/model.bin` and :code:`data/model.pickle` (if you are using the
standard configuration). Both of these files are required for the model to be
loaded back in.

*********************************
Using the model to score articles
*********************************

To use a previously-trained article-scoring model to score new articles, run:

.. code-block:: bash

   python litmon/cli/eval.py

This constructs :class:`litmon.cli.eval.ModelUser`, and outputs the scores for
the evaluation dataset (:code:`data/dbase_eval.csv`) to :code:`data/scores.npy`
(if you are using the standard configuration).

*****************************
Identifying relevant articles
*****************************

To write the top-scoring (most relevant) articles to file, use

.. code-block:: bash

   python litmon/cli/rez.py

This constructs :class:`litmon.cli.rez.ResultsWriter`, and outputs the most
relevant articles to :code:`data/results.csv`.

The number of articles written can be customized in the :code:`config/std.yaml`
file (e.g. by adding :code:`rez: {num_write: 30}` to :code:`config/std.yaml`
and calling the above script with the :code:`-f rez` flag).

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

ResultsWriter
-------------

.. autoclass:: litmon.cli.rez.ResultsWriter
