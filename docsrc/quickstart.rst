##########
Quickstart
##########

This page provides a quick reference to the commands you'll need to operate
this package. For a more in-depth look at any of these operations, see the
corresponding page of the documentation.

This page covers three main topics related to operating this package: Setting
up your environment, training your model, and identifying target articles.

All of the programs discussed below use configuration files. To learn more
about how these work, check out the :ref:`config` page. That page also
discusses how the command-line interfaces are generated for each script,
which should assist advanced users of this package.

*************
Prerequisites
*************

.. note::

   This package was developed using :code:`python3.9.7` on :code:`Ubuntu
   20.04`. For this documentation, we've aliased :code:`python=python3.9`.

#. Initialize your environment. We recommend using virtual environments.

   .. code-block:: bash

      python -m venv .venv
      source .venv/bin/activate
      python -m pip install --upgrade pip
      python -m pip install -r requirements.txt

#. If you are not the original author of this package, please update the
   :code:`user: email` field in :code:`config/std.yaml`. If you are not using
   this package for its original purpose, please update the :code:`user: tool`
   field. These can be set to any arbitrary value, and are supplied to the
   PubMed API on each query.

#. This package has a tight integration with our Azure cloud: If any data files
   are missing, then they are automatically downloaded just-in-time. To enable
   this functionality, you'll need an Azure Storage connection string, which
   you can obtain from the maintainer of this package. Place this string in
   :code:`secrets/azure`.

   The Azure integration is not requried for this pipeline to work: You can
   generate all the files and run the pipeline end-to-end without accessing our
   cloud. However, if the cloud integration is enabled, any of the following
   programs can be run in any order, and the required input files will be
   automatically pulled.

**************************
Obtaining Journal Articles
**************************

#. For this pipeline to work, you will need a list of positive (target)
   articles to use as training data.
   
   The Methuselah Foundation has provided this data in the form of electronic
   mailbox dumps, where the PubMed IDs (PMIDs) are contained within text-based
   emails.

   Currently, two such files have been provided: :code:`dump1.mbox` and
   :code:`dump2.mbox`. Place these files in the :code:`data` folder. (If you
   are integrated with the Azure cloud, these files will be automatically
   downloded as they are needed.) Then, to extract these PMIDs, run:

   .. code-block:: bash

      python litmon/cli/mbox.py

   This will save the extracted PMIDs into the :code:`data/pmids.txt` file.

   If you do NOT have access to the mailbox dump files, then you will need to
   develop your own list of positive PMIDs to use for training. Save these
   PMIDs to :code:`data/pmids.txt`, with one PMID on each line.

   For more information, check out the :ref:`mbox` page.

#. Once you have a list of positive articles, you can use that list to build a
   database of training articles.

   This package is configured to build databases on a month-to-month basis: For
   example, if you want to build a database running from January through March
   of 2020, this database will be output to 3 files, one for each month.

   You can specify the included months in the :code:`fit_dates: date_range`
   variable in :code:`config/std.yaml`. Then, you can build the databases with:
   
   Each database file will be balanced to a set ratio between negative and
   positive articles.

   To generate your databses, run:

   .. code-block:: bash

      python litmon/cli/dbase.py
   
   This will output your databases to :code:`data/*-fit.csv` files. (E.g. The
   fitting data for Januaray 2020 will be output to
   :code:`data/2020-01-fit.csv`.)

   For more information, check out the :ref:`dbase` page.

#. After building a database of training articles, you will then need to build
   a database of testing articles. This is similar to the previous step, but
   the database will NOT be balanced.

   You can specify the included months in the :code:`eval_dates: date_range`
   variable. Then, you can build the databases with:

   .. code-block:: bash

      python litmon/cli/dbase_eval.py
   
   This will output your databases to :code:`data/*-eval.csv` files. (E.g. The
   evaluation data for February 2020 will be output to
   :code:`data/2020-02-eval.csv`.)
   
   For more information, check out the :ref:`dbase` page.

***************************
Identifying Target Articles
***************************

#. To train a model for identifying positive (target) articles, run:

   .. code-block:: bash

      python litmon/cli/fit.py

   Your model will be output to :code:`data/model.bin` and
   :code:`data/model.pickle`. (Both files are required for your model to run.)

   For more information, check out the :ref:`model` page.

#. To identify positive articles in testing data, run:

   .. code-block:: bash

      python litmon/cli/eval.py

   This script uses the same evaluation article date range as the
   :code:`dbase_eval` script. The most relevant articles for each month will be
   written to :code:`data/*-results.xlsx` (E.g. The results data for February
   2020 will be output to :code:`data/2020-02-results.csv`.)

   For more information, check out the :ref:`model` page.
