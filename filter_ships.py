#!/usr/bin/env python3

import csv
import time

import dxcluster

class Interesting(object):
    def __init__(self):
        self.calls = dict()   # call/str => info/str
        with open("ships.csv", newline="") as csvfile:
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
recently_seen = RecentlySeen()
interesting = Interesting()

for spot in dxcluster.spots(CALL, (HOST, PORT)):
    if not interesting.accept(spot.dx):
        continue
    tup = (spot.dx, spot.freq,)
    if recently_seen.is_seen(tup):
        continue
    info = interesting.info(spot.dx)
    print(f"{spot.time:<6}{spot.dx:<9s}{spot.freq:>8}  {info}  (spotted by {spot.spotter})")
