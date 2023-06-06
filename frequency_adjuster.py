#!/usr/bin/env python3

import math
import re
import socket
import statistics
import time

import dxcluster

HOST = 'rbn.telegraphy.de'    # The remote host
PORT = 7000              # The same port as used by the server
CALL = 'SM5OUU'

class SpotAverage(object):
    """Keep the average of a certain spot"""
    def __init__(self, dx):
        self.dx = dx
        self.spotters = dict()

    def adjust(self, spotter, freq):
        if spotter in self.spotters:
            offset = freq - self.spotters[spotter]
            if abs(offset) > 0.01:
                # QSY detected if one spotter moves it
                self.spotters = dict()
                print(self.dx, "qsy", offset)
        if len(self.spotters) > 0:
            offset = freq - statistics.mean(self.spotters.values())
            if abs(offset) > 1:
                # QSY detected by new spotter
                self.spotters = dict()
                print(self.dx, "qsy on new spotter", offset)
        self.spotters[spotter] = freq
        return statistics.mean(self.spotters.values())

def band(freq):
    # FIX: real calculation
    return "ALL"

def top_adjustments(d):
    return sorted([(abs(adj), val, adj) for val,adj in d.items()],
                  reverse=True)[:3]


count = 0
dxes = dict()
spotter_adjustments = dict() # (str, band) => float
total = 0
for spot in dxcluster.spots(CALL, (HOST, PORT)):
    count = count + 1
    if count % 100 == 0:
        print(count, "spots filtered", "total", len(dxes), "monitored")
        print(top_adjustments(spotter_adjustments))
        print("total drift:", total)
    spotter_band = (spot.spotter, band(spot.freq))
    if spotter_band not in spotter_adjustments:
        spotter_adjustments[spotter_band] = 0.0
    adjusted_frequency_1 = spot.freq + spotter_adjustments[spotter_band]
    if spot.dx not in dxes:
        dxes[spot.dx] = SpotAverage(spot.dx)
    adjusted_frequency_2 = dxes[spot.dx].adjust(spot.spotter, adjusted_frequency_1)
    freq_diff = adjusted_frequency_2 - spot.freq
    total += freq_diff
    adjusted_frequency_3 = adjusted_frequency_2 - total / 1000
    spotter_adjustments[spotter_band] += (adjusted_frequency_2 - adjusted_frequency_1) / 10
    spotout = spot.spotter + ":"
    print(f"DX de {spotout:<15s}",
          f"{adjusted_frequency_2:>9.3f}",
          f"{spot.dx:<14}", spot.rest)
