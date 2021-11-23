"""Convenience CLI w/ default reading eval config"""

from litmon.cli.dbase import DBaseBuilder
from litmon.utils import cli


# command-line interface
if __name__ == '__main__':
    config = cli(
        cls='litmon.cli.dbase.DBaseBuilder',
        description='Build database of articles',
        default=['query', 'user', 'eval_dates', 'dbase_eval'],
    )
    DBaseBuilder(**config)
