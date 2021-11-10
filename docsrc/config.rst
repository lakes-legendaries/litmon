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
     email:,  # your email address
     tool:,  # name of your program (arbitrary)
   }

   # date limits
   dates: {
     fit_start: 'YYYY/MM/DD', # if None: date of first positive article
     eval_start: 'YYYY/MM/DD',  # cutoff date between fit/eval datasets
     eval_end: 'YYYY/MM/DD',  # if None: date of last positive article
   }

   # input/output filenames
   fname: {
     dbase: '',
     eval: '',
     fit: '',
     mbox: [],  # list of mbox files
     pmids: '',
     pos: '',
   }

   # extra kwargs supplied to the specified module
   kwargs: {
     dbase: {},
     mbox: {},
     pos: {},
     query: {},
     split: {},
   }

   # PubMed query for negative articles
   query: ''
