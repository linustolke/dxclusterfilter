HOST = 'rbn.telegraphy.de'    # The remote host
PORT = 7000              # The same port as used by the server
CALL = 'SM5OUU'

import dxcluster

def add_argument(parser):
    parser.add_argument("--rbn", action='store_true', default=False,
                        help='Fetch data from rbn')

def add(args):
    if args.rbn:
        return [dxcluster.spots(CALL, (HOST, PORT))]
    else:
        return []
    
