############################
Build a Database from PubMed
############################

After obtaining a list of positive articles, you'll need to build a database of
positive and negative articles to use for training your machine learning model.

To do so, this class/script uses a pre-defined PubMed query that is `supposed`
to encompass all the positive articles. This query looks for keywords and
topics relevant to the Methuselah Foundation's goals, but pulls a lot of false
postives when it is run. (The people they hire to monitor the scientific
literature actually use this query to pull tons of articles, and select the
positive articles from there.)

This pre-defined PubMed query is used to generate a database of articles from
the date of the first positive article to the date of the last positive
article.

The resulting database can be quite large (several gigabytes in size).

Date limits can be put on this database via the :code:`config/std.yaml` configuration file. More details are given about configuration files on the :ref:`config` page.

*************
API Reference
*************

.. autofunction:: litmon.dates.get_date

.. autofunction:: litmon.dates.get_dates

.. autoclass:: litmon.dbase.DBaseBuilder
    :show-inheritance:
