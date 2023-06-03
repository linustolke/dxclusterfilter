#!/usr/bin/env python3

import csv
import re
import socket
import time

class Interesting(object):
    def __init__(self):
        self.ships = dict()
        with open("ships.csv", newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in reader:
                print("Showing", row)
                call = row[0].strip()
                self.ships[call] = ({
                    "callsign":call,
                    "name":row[1].strip(),
                    "type": row[2].strip(),
                    "location": row[3].strip(),
                })

    def call(self, call):
        if call in self.ships:
            return self.ships[call]
        # return {
        #     "callsign":call,
        #     "name":"Spotted station " + call,
        #     "type":"Spot",
        #     "location":"reverse beacon network",
        # }
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

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    data = s.recv(1024).decode()
    print('Connected', data)
    print(CALL)
    s.sendall(CALL.encode() + b'\r\n')
    count = 0
    while True:
        count = count + 1
        if count % 1000 == 0:
            print(count, "spots filtered")
        data = s.recv(1024).decode().strip()
        if not data:
            break
        m = re.match(r"DX de ([^:]*):[ \t][ \t]*([1-9][0-9]*(.[0-9][0-9]*)?)[ \t][ \t]*([^ ]*)  *.*$",
                     data)
        if m:
            found = interesting.call(m.group(4))
            if not found:
                continue
            tup = (m.group(4), m.group(2),)
            if recently_seen.is_seen(tup):
                continue
            print(f"{m.group(4):<9s}{m.group(2):>8}  {found['name']} {found['type']} {found['location']}  (spotted by {m.group(1)})")
