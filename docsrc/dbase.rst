.. _dbase:

##################
Building Databases
##################

This package contains utilities for pulling journal articles databases using
the PubMed API.

To do this, we use the :code:`pymed` package, which extracts the following fields for each article:

.. code-block:: python

   abstract
   authors
   conclusions
   copyrights
   doi
   journal
   keywords
   methods
   publication_date
   pubmed_id
   results
   title

Not all fields are filled out for all articles.

*****************
Pulling Positives
*****************

Once you have a list of positive PubMed IDs (saved to :code:`data/pmids.txt`),
you can pull the full corresponding article information from PubMed. While this
isn't a required step in the modeling pipeline, it does give you a good look at
the data.

You can do this using the :code:`litmon.cli.pos` script:

.. code-block:: bash

   python litmon/cli/pos.py

This constructs :class:`litmon.cli.pos.PositiveQuerier`, using the
:code:`user` field from :code:`config/std.yaml`, and outputs the positive
articles to :code:`data/positive_articles.csv` (if you are using the standard configuration).

************************
Building Train/Test Sets
************************

To train a model, you'll need both positive (target) and negative (non-target)
articles. You'll need both of these in both fitting (training) and evaluation
(testing) sets.

To build a dataset, use the :code:`litmon.cli.dbase` module. This module uses
a pre-defined PubMed query (specified in :code:`std/config.yaml`) that is
`supposed` to encompass all the positive articles. This query looks for
keywords and topics relevant to the Methuselah Foundation's goals, but pulls a
lot of false postives when it is run. (The people they hire to monitor the
scientific literature actually use this query to pull tons of articles, and
select the positive articles from there.) So, by pulling all artilces using
this query, you're getting a true dataset that could work in a real-world
scenario.

Each set consists of all articles that match the given query (specified in your
config yaml file) within date bounds you set (also specified in your config
yaml file). More details are given about configuration files on the
:ref:`config` page.

The resulting database can be quite large (several gigabytes in size).

Training Set
------------

To build a training set, use:

.. code-block:: bash

   python litmon/cli/dbase.py

This constructs :class:`litmon.cli.dbase.DBaseBuilder`, using the
:code:`query`, :code:`user`, and :code:`dbase_fit` fields from
:code:`config/std.yaml`, and outputs the training database to
:code:`data/dbase_fit.csv` (if you are using the standard configuration).


Testing Set
-----------

To build a training set, use:

.. code-block:: bash

   python litmon/cli/dbase.py -f query user dbase_eval

This constructs :class:`litmon.cli.dbase.DBaseBuilder`, using the
:code:`query`, :code:`user`, and :code:`dbase_eval` fields from
:code:`config/std.yaml`, and outputs the testing database to
:code:`data/dbase_eval.csv` (if you are using the standard configuration).

*************
API Reference
*************

PubMedQuerier
-------------

.. autoclass:: litmon.query.PubMedQuerier
   :members: query

Date Parsing
------------

.. autofunction:: litmon.utils.dates.get_date

.. autofunction:: litmon.utils.dates.get_dates

PositiveQuerier
---------------

.. autoclass:: litmon.cli.pos.PositiveQuerier
   :show-inheritance:

DBaseBuilder
------------

.. autoclass:: litmon.cli.dbase.DBaseBuilder
    :show-inheritance:
