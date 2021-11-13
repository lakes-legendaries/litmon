"""command line interface helper"""

from argparse import ArgumentParser
from typing import Any

import yaml


def cli(
    cls: str,
    description: str,
    default: list[str],
) -> dict[str, Any]:
    """Create CLI that loads kwargs from config files

    Parameters
    ----------
    cls: str
        Class to be constructed from configuration parameters.
        This is only used as a :code:`help` prompt.
    description: str
        Description of the program, printed out if the user uses the :code:`-h`
        flag
    default: list[str]
        Default fields to use from file (if not overridden by user)

    Returns
    -------
    dict
        All parameters loaded from all supplied configuration files
    """

    # parse command-line arguments
    parser = ArgumentParser(description)
    parser.add_argument(
        '-c',
        '--config_fname',
        default='config/std.yaml',
        help='Configuration yaml file',
    )
    parser.add_argument(
        '-f',
        '--fields',
        default=default,
        nargs='+',
        help=f'Unpack these files in config_fname to construct {cls}'
    )
    args = parser.parse_args()

    # load configuration file
    config = yaml.safe_load(open(args.config_fname, 'r'))

    # unpack fields
    out = {}
    for field in args.fields:
        if type(config[field]) is dict:
            out = out | config[field]
        else:
            out[field] = config[field]

    # return
    return out
