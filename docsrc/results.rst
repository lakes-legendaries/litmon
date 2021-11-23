#######
Results
#######

************
Results List
************

Results from running this algorithm can be downloaded from any of the links
below. These files list the top-scoring (most relevant) articles that the
algorithm found in the specified time periods.

.. raw:: html

    <iframe
        src="https://mfoundation.blob.core.windows.net/litmon/directory.html"
        height="150px"
        width="200px"
    >
    </iframe>

|

Most fields in this document should be self-explanatory. If a field is empty,
it's because the information wasn't available through the PubMed API.

***************
Tracking Fields
***************

Three fields are used for tracking model performance: :code:`score`,
:code:`label`, and :code:`feedback`.

The :code:`score` field is the score assigned to the article by the model.
Higher scores mean an article is more relevant. (This is the parameter that
:code:`thresh` is checked against in :class:`litmon.cli.rez.ResultsWriter`.)
The highest-scoring articles are included in each results file.

The :code:`label` field is whether an article was identified by the people
hired by the Methuselah Foundation as being relevant to the foundation's
mission. (I.e. the label is :code:`True` iff the PMID of the article is
included in :code:`data/pmids.txt`).

The :code:`feedback` field is a place for a manual reviewer to provide feedback
on whether they think the article is relevant. We recommend scoring articles on
a 0-2 basis (0=reject, 1=include, 2=super relevant). Non-integer scores are OK.
In the future, we hope to expand this package to train on this feedback field
in addition to the provided pmid list.

*******************
Baseline Comparison
*******************

Some of the results files include a :code:`Missed Articlces` sheet, which lists
all articles that were flagged by the people hired by the Methuselah
Foundation, but were NOT identified by the model.

The model can be made to identify/include any of these articles by increasing
the :code:`count` variable or setting the :code:`thresh` variable in
:class:`litmon.cli.eval.ModelUser`. Any significant change could lead to a much
larger number of articles being identified/included in the results files.

*****************
Technical Details
*****************

All results currently listed were created through the :code:`config/std.yaml`
script, which used a model that was trained on data from 2013/01/01 through
2017/12/31 (YYYY/mm/dd). This model was then used to identify the top-scoring
articles from each month of 2019 and 2020.
