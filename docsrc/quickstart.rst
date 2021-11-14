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

***************************
Setting Up Your Environment
***************************

To use this package, you'll need to setup your python environment and generate
or obtain the required data files.

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
   :code:`user::email` field in :code:`config/std.yaml`. If you are not using
   this package for its original purpose, please update the :code:`user::tool`
   field. These can be set to any arbitrary value, and are supplied to the
   PubMed API on each query.

#. For this pipeline to work, you will need a list of positive (target)
   articles to use as training data.
   
   The Methuselah Foundation has provided this data in the form of mailbox
   dumps, where the PubMed IDs (PMIDs) are contained within text-based emails.

   Currently, two such files have been provided. Place these files in the data
   folder, naming them :code:`dump1.mbox` and :code:`dump2.mbox`. (It does not
   matter which is which.) Then, to extract these PMIDs, run:

   .. code-block:: bash

      python litmon/cli/mbox.py

   This will save the extracted PMIDs into the :code:`data/pmids.txt` file.

   If you do NOT have access to the mailbox dump files, then you will need to
   develop your own list of positive PMIDs to use for training. Save these
   PMIDs to :code:`data/pmids.txt`, with one PMID on each line.

   For more information, check out the :ref:`mbox` page.

#. (Optional) To pull all the data associated with each positive article, run:

   .. code-block:: bash

      python litmon/cli/pos.py

   This will pull the positive articles using the :code:`pymed` package, saving
   them to :code:`data/positive_articles.csv`.

   For more information, check out the :ref:`dbase` page.

*******************
Training Your Model
*******************

Once you've set up your environment, you'll need to train a model to
discriminate between positive (target) and negative (non-target) articles.

#. First, you'll need to build a database of positive and negative articles,
   using the pmid list you created (above). Set the date bounds of your
   database by specifying the :code:`min_date` and :code:`max_date` (in the
   :code:`dbase_fit` dictionary) in your :code:`config/std.yaml` file. Then,
   build the database with:

   .. code-block:: bash

      python litmon/cli/dbase.py
   
   This will output your database to :code:`data/dbase_fit.csv`. Progress will
   be logged to :code:`logs/dbase_fit.log`.

   For more information, check out the :ref:`dbase` page.

#. Next, train your model with:

   .. code-block:: bash

      python litmon/cli/fit.py

   Your model will be output to :code:`data/model.bin` and
   :code:`data/model.pickle`. (Both files are required for your model to run.)

   For more information, check out the :ref:`model` page.

***************************
Identifying Target Articles
***************************

Now that you've trained your model, you can use it to identify relevant
articles in the scientific literature.

#. First, build a database of articles to use your trained model on. The date
   bounds for this article can be set in the :code:`config/std.yaml` file, by
   modifying the :code:`min_date` and :code:`max_date` in the
   :code:`dbase_eval` dictionary. Create this database with:

   .. code-block:: bash

      python litmon/cli/dbase.py -f query user dbase_eval
   
   This will output your database to :code:`data/dbase_eval.csv`. Progress will
   be logged to :code:`logs/dbase_eval.log`.

   For more information, check out the :ref:`dbase` page.

#. Next, score the articles in your databse with:

   .. code-block:: bash

      python litmon/cli/eval.py
   
   This will output scores to :code:`data/scores.npy`.

   For more information, check out the :ref:`model` page.

#. Finally, write the most relevant articles to file with:

   .. code-block:: bash

      python litmon/cli/rez.py

   The most relevant articles will be written to :code:`data/results.xlsx`.

   For more information, check out the :ref:`model` page.
