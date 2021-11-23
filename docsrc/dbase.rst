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

For this article-identifying pipeline to work, you'll need both positive
(target) and negative (non-target) journal articles. You'll need both of these
in both fitting (training) and evaluation (testing) sets.

To build datasets, use the :code:`litmon.cli.dbase` module. This module uses a
pre-defined PubMed query (specified in :code:`std/config.yaml`) that is
`supposed` to encompass all the positive articles. This query looks for
keywords and topics relevant to the Methuselah Foundation's goals, but pulls a
lot of false postives when it is run. (The people they hire to monitor the
scientific literature actually use this query to pull tons of articles, and
select the positive articles from there.) So, by pulling all articles using
this query, you're getting the real data that the Methuselah Foundation's
employees use to find relavent articles (i.e. this is completely a real-world
scenario).

Databases are constructed on a month-to-month basis. E.g. If you are
constructing fitting databases using the date range :code:`2020/01-2020/03`,
you'll get three database files:

#. :code:`data/2020-01-fit.csv`
#. :code:`data/2020-02-fit.csv`
#. :code:`data/2020-03-fit.csv`

The date range can be set by modifying the :code:`date_range` variable in the
:code:`fit_dates` and/or :code:`eval_dates` dictionary in
:code:`config/std.yaml`.

******************
Training Databases
******************

Training databases are automatically balanced, using :code:`balance_ratio` in
:class:`litmon.cli.dbase.DBaseBuilder`. E.g. if the :code:`balance_ratio` is 3,
then each training databse will have 3 negative articles for every positive
article. (The value for this can be overriden by adding :code:`balance_ratio`
to the :code:`dbase_fit` dictionary in :code:`config/std.yaml`.)

To build a training database, use:

.. code-block:: bash

   python litmon/cli/dbase.py

This constructs :class:`litmon.cli.dbase.DBaseBuilder`, using the
:code:`query`, :code:`user`, :code:`fit_dates`, and :code:`dbase_fit` fields
from :code:`config/std.yaml`, and outputs the training databases to
:code:`data/*-fit.csv` files (if you are using the standard configuration).

*****************
Testing Databases
*****************

Testing databases are NOT balanced, but are otherwise similar to training
databases. To construct testing databases, use:

.. code-block:: bash

   python litmon/cli/dbase_eval.py

This constructs :class:`litmon.cli.dbase.DBaseBuilder`, using the
:code:`query`, :code:`user`, :code:`eval_dates`, and :code:`dbase_eval` fields
from :code:`config/std.yaml`, and outputs the testing databases to
:code:`data/*-eval.csv` (if you are using the standard configuration).

.. note::

   :code:`litmon/cli/dbase_eval.py` uses
   :class:`~litmon.cli.dbase.DBaseBuilder` from :code:`litmon/cli/dbase.py`.
   (It's a simple wrapper for :code:`DBaseBuilder` that defaults to the
   :code:`eval_dates` and :code:`dbase_eval` fields, instead of the
   :code:`fit_dates` and :code:`dbase_fit` fields.)

*************
API Reference
*************

PubMedQuerier
-------------

.. autoclass:: litmon.query.PubMedQuerier
   :members: query

Date Parsing
------------

.. autofunction:: litmon.utils.dates.drange

DBaseBuilder
------------

.. autoclass:: litmon.cli.dbase.DBaseBuilder
    :show-inheritance:
