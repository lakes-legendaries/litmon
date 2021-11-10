################################
Pull Target Articles from PubMed
################################

Once we have a list of positive PubMed IDs, we need to pull the full
corresponding article information from PubMed.

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

*************
API Reference
*************

.. autoclass:: litmon.query.PubMedQuerier
   :members: query

.. autoclass:: litmon.pos.PositiveQuerier
   :show-inheritance:
