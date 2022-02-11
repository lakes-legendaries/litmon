.. _config:

#################################
Understanding Config Files & CLIs
#################################

********
Overview
********

This package uses a common function for parsing configuration files and
generating command-line interfaces: The :meth:`litmon.utils.cli.cli` method.

This method is used in each script file (i.e. each file in :code:`litmon.cli`)
with a code block that looks like:

.. code-block:: python

   if __name__ == '__main__':
       config: dict = cli(...)
       cls(**config)

This methods creates a command-line interface (cli) that takes two parameters:

#. :code:`-c,--config_fname`: the name of the configuration yaml file

#. :code:`-f,--fields`: the name of the fields in the file to unpack

Then, when the script containing the above code block is called from the
command line, this function loads the configuration file and unpacks the listed
fields as :code:`kwargs`, which are used to construct :code:`cls` (more details
on this below).

********
Example
********

If your file configuration file looks like

.. code-block:: python

   nouns: {
       animal: dog,
       superhero: ironman,
   }
   verbs: {
       past: ran,
       present: runs,
   }
   adjectives: {
       color: blue,
       size: small,
   }

and you use this function to create a cli that is called via

.. code-block:: bash

    python program.py -f nouns verbs

Then this function will return a dictionary that looks like

.. code-block:: python

   {
       animal: dog,
       superhero: ironman,
       past: ran,
       present: runs,
   }

and those variables will be unpacked to construct :code:`cls`.

This setup lets you have one `main` configuration file that you can
pick-and-choose fields from on a program-by-program basis.

*************
Non-dict args
*************

If any of the fields this function tries to unpack are NOT dictionaries,
then the field is used as-is. E.g. if your yaml configuration file contains

.. code-block:: python

   fname: test.bin

and you unpack the :code:`fname` variable

.. code-block:: bash

   python program.py -f fname

Then this function will return the dictionary

.. code-block:: python

   {
       fname: test.bin,
   }

****************
Constructing cls
****************

The unpacked arguments are used to construct :code:`cls` in each
:code:`litmon.cli` file. :code:`cls` is the only class in that given file.

This is the extent of the command-line interface: Each :code:`cls` runs a class
as a script on construction. This is object-oriented code that is used as
simple python scripts. The reason behind this is that then it is easy to
inherit a new subclass that customizes the implementation, while still
maintaining the same simple and clean command line interface.

*************
API Reference
*************

.. autofunction:: litmon.utils.cli.cli
