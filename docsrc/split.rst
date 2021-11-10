################################
Create Fitting & Evaluation Sets
################################

After building a database, that database must be split into fitting and
evaluation (training and testing) datasets.

All articles in the fitting set happen before some arbitrarily-chosen cutoff
date (specified in the config file :code:`config/std.yaml`; see the
:ref:`config` page for more details). All articles in the evaluation set happen
on or after the cutoff date.

To build the fitting set, articles are pulled iff:

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

The evaluation set is simpler: All articles on or after the cutoff date are
included. This thus provides a real-world test of the data: All articles pulled
by the query are included for evaluation.

*************
API Reference
*************

.. autoclass:: litmon.split.Splitter
