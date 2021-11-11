##########
Quickstart
##########

This page provides a quick reference to the commands you'll need to operate
this package. For a more in-depth look at any of these operations, see the
corresponding page of the documentation.

.. note::

   This package was developed using :code:`python3.9.7` on :code:`Ubuntu
   20.04`. For this documentation, we've aliased :code:`python=python3.9`.

#. Initialize your environment. We recommend using virtual environments.

   .. code-block:: bash

      python -m venv .venv
      source .venv/bin/activate
      python -m pip install --upgrade pip
      python -m pip install -r requirements.txt

#. For this pipeline to work, you will need a list of positive (target)
   articles to use as training data.
   
   The Methuselah Foundation has provided this data in the form of mailbox
   dumps, where the PubMed IDs (PMIDs) are contained within text-based emails.

   Currently, two such files have been provided. Place these files in the data
   folder, naming them :code:`dump1.mbox` and :code:`dump2.mbox`. (It does not
   matter which is which.) Then, to extract these PMIDs, run:

   .. code-block:: bash

      python litmon/mbox.py

   This will save the extracted PMIDs into the :code:`data/pmid.txt` file.

   If you do NOT have access to the mailbox dump files, then you will need to
   develop your own list of positive PMIDs to use for training. Save these
   PMIDs to :code:`data/pmid.txt`, with one PMID on each line.

#. The next step is to pull the full journal article for each positive PMID. To
   do so, run:

   .. code-block:: bash

      python litmon/pos.py

   This will pull the positive articles using the :code:`pymed` package, saving
   them to :code:`data/pos.csv`.

#. Next, you will need to build a database of positive and negative (target and
   non-target) articles to train your model. Negative articles are pulled that
   match the date range of your positive articles, and are pulled via a PubMed
   query provided in :code:`config/std.yaml`.

   .. code-block:: bash

      python litmon/dbase.py

   Progress is logged to :code:`logs/dbase.log`. The resulting database in
   output to :code:`data/dbase.csv`.

#. Create fitting and evaluating sets from your database with:

   .. code-block:: bash

      python litmon/split.py

   This will create a :code:`data/fit.csv` file and a :code:`data/eval.csv`
   file.

#. Vectorize the articles in your fitting/evaluation sets with:

   .. code-block:: bash

      python litmon/vec.py
   
   This will output your vectorized documents to :code:`data/fit.npy` and
   :code:`data/eval.npy`.

#. Build ML models to score the articles in the evaluation set with:

   .. code-block:: bash

      python litmon/model.py

   The scores for the evaluation set are written to
   :code:`data/eval_scores.npy`.
