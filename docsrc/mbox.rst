############################
Extract PMIDs from Mailboxes
############################

The Methuselah Foundation has, for several years, paid people to read
aging-related PubMed articles, and to bring the best ones to the attention of
the leadership of the foundation. This has typically been communicated through
email.

To create a dataset of target articles, we've written a script that extract the
PubMed IDs for positive (target) article from mailbox dumps of these emails.

This results in a list of PubMed IDs, e.g.

.. code-block:: python

   12345678
   12345679
   12345680
   ...
   98765432

If you still want to use this package, but don't have access to these email
dumps, then make your own list of PMIDs in the above format.

*************
API Reference
*************

.. autoclass:: litmon.mbox.PubMedIDExtractor
    :members: to_file
