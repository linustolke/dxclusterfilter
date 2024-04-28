

def add_argument(parser):
    parser.add_argument("--ft8", action='store_true', default=False,
                        help='Fetch data from FT8')

def spots():
    if False:
        yield None
    pass

def add(args):
    if args.ft8:
        return [spots()]
    else:
        return []

