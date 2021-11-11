.. _config:

##########################
Understanding Config Files
##########################

Each of the command-line interfaces takes one parameter,
:code:`-c,--config_fname`, which is the name of the file containing the
configuration to run. This defaults to :code:`config/std.yaml` for all scripts.

This configuration file provides basic filenames and governing parameters to be
used by the programs.

The information expected to be supplied in this file includes:

.. code-block:: python

   # required by the pubmed api
   user: {
     email: str,  # your email address
     tool: str,  # name of your program (arbitrary)
   }

   # date limits, all w/ format YY-mm-dd
   dates: {
     fit_start: str,  # if None: date of first positive article
     eval_start: str,  # cutoff date between fit/eval datasets
     eval_end: str,  # if None: date of first positive article
   }

   # input/output filenames
   fname: {
     dbase: str,
     eval_csv: str,
     eval_npy: str,
     eval_scores: str,
     fit_csv: str,
     fit_npy: str,
     mbox: list[str],  # list of mbox dumps
     pmids: str,
     pos: str,
     vec_eval: str,
     vec_fit: str,
   }

   # extra kwargs supplied to the specified module
   kwargs: {
     dbase: dict[str, Any],
     mbox: dict[str, Any],
     model: dict[str, Any],
     pos: dict[str, Any],
     query: dict[str, Any],
     split: dict[str, Any],
   }

   # PubMed query for negative articles
   query: str
