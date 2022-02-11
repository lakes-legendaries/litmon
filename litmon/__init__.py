"""Literature Monitoring Project, for the Methuselah Foundation

The :module:`litmon.query` module contains a basic PubMed querier.

The :module:`litmon.model` module contains a model for vectorizing journal
articles and scoring them (i.e. predicting their relevance to the mission of
the Methuselah Foundation).

The :module:`litmon.utils` folder contains common utilities used throughout
this project.

The :module:`litmon.cli` folder contains simple command line interfaces for
this package's major functionalities.
"""

# flake8: noqa

from litmon.model import ArticleScorer
from litmon.query import PubMedQuerier


__version__ = '0.0.22'
