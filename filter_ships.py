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

class Reader(object):
    def __init__(self, stream):
        self.buffer = ''
        self.stream = stream

    def readline(self):
        while True:
            end_of_line = self.buffer.find('\n')
            if end_of_line >= 0:
                first_line = self.buffer[0:end_of_line]
                self.buffer = self.buffer[end_of_line + 1:]
                return first_line
            chunk = self.stream.recv(2048)
            if not chunk:
                return None
            self.buffer += chunk.decode()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    reader = Reader(s)
    print(reader.readline())
    s.sendall(CALL.encode() + b'\r\n')
    print(reader.readline())
    s.sendall(b'set/raw\r\n')
    count = 0
    while True:
        data = reader.readline()
        if data == None:
            break
        count = count + 1
        if count % 1000 == 0:
            print(count, "spots filtered")
        REGEXP_PART1 = r"DX de ([^:]*):\s+"
        REGEXP_PART2 = r"([0-9]+(.[0-9]+)?)\s+"
        REGEXP_PART3 = r"([^ ]+)\s+"
        REGEXP_PART4 = r"(CW|PSK31|PSK63|RTTY)\s+"
        REGEXP_PART5 = r"-?[0-9]*\s+dB\s+"
        REGEXP_PART6 = r"[1-9][0-9]*\s+(WPM|BPS)\s+"
        REGEXP_PART7 = r"(BEACON|CQ|DX|NCDXF B)\s+([0-9]*Z).*$"
        m = re.match(REGEXP_PART1 + REGEXP_PART2 + REGEXP_PART3 +
                     REGEXP_PART4 + REGEXP_PART5 + REGEXP_PART6 +
                     REGEXP_PART7,
                     data)
        if m:
            found = interesting.call(m.group(4))
            if not found:
                continue
            tup = (m.group(4), m.group(2),)
            if recently_seen.is_seen(tup):
                continue
            print(f"{m.group(8):<6}{m.group(4):<9s}{m.group(2):>8}  {found['name']} {found['type']} {found['location']}  (spotted by {m.group(1)})")
        else:
            print("Not parsed", data)
            m = re.match(REGEXP_PART1,
                         data)
            if m:
                print("DEBUG:","match 1", m.group(0))
                m = re.match(REGEXP_PART1 + REGEXP_PART2,
                             data)
                if m:
                    print("DEBUG:","match 2", m.group(0))
                    m = re.match(REGEXP_PART1 + REGEXP_PART2 + REGEXP_PART3,
                                 data)
                    if m:
                        print("DEBUG:","match 3", m.group(0))
                        m = re.match(REGEXP_PART1 + REGEXP_PART2 +
                                     REGEXP_PART3 + REGEXP_PART4,
                                     data)
                        if m:
                            print("DEBUG:","match 4", m.group(0))
                            m = re.match(REGEXP_PART1 + REGEXP_PART2 +
                                         REGEXP_PART3 + REGEXP_PART4 +
                                         REGEXP_PART5,
                                         data)
                            if m:
                                print("DEBUG:","match 5", m.group(0))
                                m = re.match(REGEXP_PART1 + REGEXP_PART2 +
                                             REGEXP_PART3 + REGEXP_PART4 +
                                             REGEXP_PART5 + REGEXP_PART6,
                                             data)
                                if m:
                                    print("DEBUG:","match 6", m.group(0))
