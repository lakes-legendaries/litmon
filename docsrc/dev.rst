#########################
Contributing to this Repo
#########################

#. Coding standards

   #. All code should be error-free via :code:`flake8` linting.

   #. Where applicable, use :code:`pytest`-compliant unit tests.

#. Continuous Integration (CI)

   #. Documentation is automatically built through GitHub Actions, published to
      the :code:`docs` branch to keep the :code:`main` branch light.

      To test documentation, run :code:`docsrc/build`.

      Do NOT check in documentation to your branch.

   #. The version number is automatically updated through GitHub Actions on each
      push to main. With each update, the main branch is tagged with the version
      number.

#. If you are using this repo in support of the Methuselah Foundation, you may
   want to access our azure cloud, which is where we publish results and store
   private data files.
   
   To interface with the azure cloud, you'll need a connection string, which
   should be stored in your :code:`secrets/azure` file. Never check this file
   in to your repo.

   Contact the maintainer of package repo for credentials.

#. Pull requests are welcome.
