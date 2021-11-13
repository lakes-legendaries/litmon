.. _mbox:

####################
Getting Target PMIDs
####################

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

**********************
Command-Line Interface
**********************

To extract pmids, use

.. code-block:: bash

   python litmon/cli/mbox.py

This constructs :class:`litmon.cli.mbox.PubMedIDExtractor`, using the
:code:`mbox_fname` field from :code:`config/std.yaml`, and outputs the positive
pmids to :code:`data/pmids.txt` (if you are using the standard configuration).

*************
API Reference
*************

.. autoclass:: litmon.cli.mbox.PubMedIDExtractor
