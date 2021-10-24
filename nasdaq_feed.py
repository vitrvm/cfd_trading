import argparse

from cfd_trading import DukasCopy


def runstrat(args=None):
    args = parse_args(args)

    kwargs = dict()

    params = dict()

    if args.format:  # Plot if requested to
        params['format'] = args.format

    if args.filename:
        params['filename'] = args.filename

    if args.fromdate:
        params['start_date'] = args.fromdate
        
    if args.todate:
        params['finish_date'] = args.todate

    if args.ticker:
        params['ticker'] = args.ticker

    params['freq'] = 'tick'
    
    dc = DukasCopy(config=params)

def parse_args(pargs=None):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description=(
            'My parser '
            'Testing my parser')
    )

    parser.add_argument('--filename', required=True, help='filename')

    parser.add_argument('-f', '--format', required=False, default='csv', choices=['csv', 'sqlite'], help='format of save file.')

    parser.add_argument('--fromdate', default='2021-01-01', help='Starting date in YYYY-MM-DD format')

    parser.add_argument('--todate', default=None, help='End date in YYYY-MM-DD format')

    parser.add_argument('--ticker', default=None, help='ticker to access data')

    return parser.parse_args(pargs)

if __name__ == '__main__':
    runstrat()
    
    