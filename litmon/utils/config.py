"""Generate evaulation config files"""

from argparse import ArgumentParser
from datetime import datetime, timedelta

import yaml


if __name__ == '__main__':

    # description
    parser = ArgumentParser('Generate evaluation config files')

    # add arguments
    parser.add_argument(
        '-m',
        '--month',
        type=int,
        default='Month (1-12) to use as eval set',
    )
    parser.add_argument(
        '-y',
        '--year',
        type=int,
        default='Year (e.g. 2020) to use as eval set',
    )
    parser.add_argument(
        '-s',
        '--string',
        nargs='+',
        type=str,
        default=[],
        help="""
        Arbitrary string key-value pairs to add to the output config file.
        Arg 2n is a key, arg 2n+1 is the value for the preceding key.
        All values will be interpretted as strings.
        """,
    )

    # parse arguments
    args = parser.parse_args()

    # get dates
    min_date = f'{args.year}/{args.month:02d}/01'
    next_month = args.month + 1 if args.month < 12 else 1
    next_year = args.year if args.month < 12 else args.year + 1
    max_date = (
        datetime(next_year, next_month, 1).date()
        - timedelta(days=1)
    )
    max_date = f'{max_date.year}/{max_date.month:02d}/{max_date.day:02d}'

    # get output fname
    ym_text = f'{args.year}-{args.month:02d}'
    fname = f'config/{ym_text}.yaml'

    # load in std config
    std_config = yaml.safe_load(open('config/std.yaml', 'r'))

    # create dict
    config = {
        'user': std_config['user'],
        'dbase_fname': f'data/dbase_eval_{ym_text}.csv',
        'scores_fname': f'data/scores_{ym_text}.npy',
        'rez_fname': f'data/{ym_text}',
        'dbase_eval': {
            'min_date': min_date,
            'max_date': max_date,
            'log_fname': f'logs/dbase_eval_{ym_text}.log',
        },
        'query': std_config['query'],
    }

    # add in extra args
    for n in range(0, len(args.string), 2):
        config[args.string[n]] = args.string[n+1]

    # write to file
    yaml.dump(config, open(fname, 'w'))
