CLUSTERS = [
    ('sm6hoc.se', 8000, 'SM6HOC-2'),
    ('sector7.nu', 8000, 'SM6YOU-2'),
    ]
CALL = 'SM5OUU'

import dxcluster

def add_argument(parser):
    parser.add_argument("--cluster", type=int, action='append', default=[],
                        help='Connect to cluster, one of ' +
                        ', '.join([f"{nr}={tuple[2]}" for nr, tuple in enumerate(CLUSTERS)]))

def add(args):
    return [dxcluster.spots(CALL, (CLUSTERS[i][0], CLUSTERS[i][1]))
            for i in args.cluster]
