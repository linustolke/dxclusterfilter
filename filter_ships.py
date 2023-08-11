#!/usr/bin/env python3

from argparse import ArgumentParser
import csv
import html_table_parser
import re
import urllib.request
import time

import dxcluster

parser = ArgumentParser(description="Show a certain set of stations from reverse beacon network.")
parser.add_argument('--url', type=str, default=None,
                    help='The url to fetch with data')
parser.add_argument('--file', type=str,
                    help='The file where the calls to monitor are listed',
                    default="ships.csv")

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


HOST = 'rbn.telegraphy.de'    # The remote host
PORT = 7000              # The same port as used by the server
CALL = 'SM5OUU'

if __name__ == '__main__':
    args = parser.parse_args()

    recently_seen = RecentlySeen()
    interesting = Interesting()
    if args.url:
        interesting.from_url(args.url)
    else:
        interesting.from_file(args.file)

    for spot in dxcluster.spots(CALL, (HOST, PORT)):
        if not interesting.accept(spot.dx):
            continue
        tup = (spot.dx, spot.freq,)
        if recently_seen.is_seen(tup):
            continue
        info = interesting.info(spot.dx)
        print(f"{spot.time:<6}{spot.dx:<9s}{spot.freq:>8}  {info}  (spotted by {spot.spotter})")
