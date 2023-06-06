#!/usr/bin/env python3

import csv
import time

import dxcluster

class Interesting(object):
    def __init__(self):
        self.ships = dict()
        with open("ships.csv", newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in reader:
                call = row[0].strip()
                call = call.split(" ")[0]
                if call:
                    entry = ({
                        "callsign":call,
                        "name":row[1].strip() + " " + row[2].strip(),
                        "type": row[3].strip(),
                        "location": row[4].strip(),
                    })
                    self.ships[call] = entry
                    print("Showing", call, entry["name"])

    def call(self, call):
        if call in self.ships:
            return self.ships[call]
        return None

class RecentlySeen(object):
    """Keeps a register of recently seen entries to reduce repeats"""
    TIME = 10 * 60 # Ten minutes

    def __init__(self):
        self.seen = dict()
        self.array = []

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

count = 0
for spot in dxcluster.spots(CALL, (HOST, PORT)):
    count = count + 1
    if count % 1000 == 0:
        print(count, "spots filtered")
    found = interesting.call(spot.dx)
    if not found:
        continue
    tup = (spot.dx, spot.freq,)
    if recently_seen.is_seen(tup):
        continue
    print(f"{spot.time:<6}{spot.dx:<9s}{spot.freq:>8}  {found['name']} {found['type']} {found['location']}  (spotted by {spot.spotter})")
