#!/usr/bin/env python3

from argparse import ArgumentParser
import csv
import html_table_parser
import re
import sys
import time
import urllib.request

import ft8
import iterator_threads
import rbn
import cluster

parser = ArgumentParser(description="Show and possibly filter heard and seen stations.")
parser.add_argument('--url', type=str, default=None,
                    help='Show calls found in url.')
parser.add_argument('--file', type=str,
                    help='Show calls found in the file.',
                    default=None)
rbn.add_argument(parser)
ft8.add_argument(parser)
cluster.add_argument(parser)
parser.add_argument('--recently', action='store_true', default=False,
                    help='Show repeats')

class Interesting(object):
    def __init__(self):
        self.calls = dict()   # call/str => info/str

    def from_url(self, url):
        response = urllib.request.urlopen(url)
        text = response.read().decode()
        tp = html_table_parser.HTMLTableParser()
        tp.feed(text)
        for name, table in tp.named_tables.items():
            print("Table", name)
            call_column = None
            for index, header in enumerate(table[0]):
                if header in ["Call", "Call Sign", "Callsign"]:
                    call_column = index
            for row in table[1:]:
                call = row[call_column].strip()
                call = ''.join(list(filter(lambda c: c not in ['+', ' '],
                                           call)))
                info = ""
                for index, value in enumerate(row):
                    if index == call_column:
                        continue
                    if re.search("You need JavaScript enabled to view", value):
                        continue
                    info += " " + value.strip()
                info = info.strip()
                self.calls[call] = info
                print("Showing", call, info)

    def from_file(self, filename):
        with open(filename, newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in reader:
                call = row[0].strip()
                call = call.split(" ")[0]
                if call:
                    name = (row[1].strip() + " " + row[2].strip()).strip()
                    info = f"{name} {row[3].strip()} {row[4].strip()}"
                    self.calls[call] = info
                    print("Showing", call, info)

    def info(self, call):
        if call in self.calls:
            return self.calls[call]
        return None

    def accept(self, call):
        return call in self.calls

class RecentlySeen(object):
    """Keeps a register of recently seen entries to reduce repeats"""
    TIME = 10 * 60 # Ten minutes

    def __init__(self):
        print("Shows the same call on the same frequency only once every",
              self.TIME / 60, "minutes.")
        self.seen = dict()  # tuple => time
        self.array = []     # tuple

    def is_seen(self, x):
        result = False
        if x in self.seen and time.time() - self.seen[x] < self.TIME:
            result = True
        if x in self.array:
            self.array.remove(x)
        while len(self.array) > 0 and time.time() - self.seen[self.array[0]] > self.TIME:
            self.seen.pop(self.array[0])
            self.array = self.array[1:]
        self.seen[x] = time.time()
        self.array.append(x)
        assert len(self.seen) == len(self.array)
        return result


if __name__ == '__main__':
    args = parser.parse_args()

    if not args.recently:
        recently_seen = RecentlySeen()
    interesting = None
    if args.url:
        interesting = Interesting()
        interesting.from_url(args.url)
    if args.file:
        if interesting:
            print("Cannot specify both url and file", file=sys.stderr)
            sys.exit(1)
        interesting = Interesting()
        interesting.from_file(args.file)

    spot_iterators = []
    spot_iterators += rbn.add(args)
    spot_iterators += ft8.add(args)
    spot_iterators += cluster.add(args)

    if not spot_iterators:
        print("No indata specified")
        exit(1)

    for spot in iterator_threads.chain(*spot_iterators):
        info = ""
        if interesting:
            if not interesting.accept(spot.dx):
                continue
            info = interesting.info(spot.dx)
        if not args.recently:
            tup = (spot.dx, spot.freq,)
            if recently_seen.is_seen(tup):
                continue
        print(f"{spot.time:<6}{spot.dx:<9s}{spot.freq:>8} {spot.type:4} {info}  (spotted by {spot.spotter})")
