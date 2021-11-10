##################
Vectorize Articles
##################

Generally speaking, machine learning models need numeric data to work. So, we
create a numeric representation of each article in our training and testing
sets.

The vectorization is performed with the `vhash
<https://lakes-legendaries.github.io/vhash/>`_ package.

*************
API Reference
*************

.. autoclass:: litmon.vec.Vectorizer
