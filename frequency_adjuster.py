#!/usr/bin/env python3

"""Frequency-adjusting filter

I have noticed that sometimes the same spot shows up with different
frequencies.  Is this because the spotters are varying a little in
frequency.  If so, it should be possible to calculate how much each
spotter deviates from the others and then adjust each spot's frequency
based on that.

Important thing to check for this to work:
That the program can use more precise frequencies.


Assumptions

Spotters deviate the same amount on the same band.  If the move around
a little, that is a slow move, comparable to a frequency drift.

Spotted station most of the time stay on the same frequency.  If they
change the frequency enough to be detected by any spotter that is
handled as QSY-ing.


Current Limitations

Each spotted station can only work on one frequency at the time.


Logic

To calculate the spotter offset, for each spot, calculate the
difference between the spot's frequency from that spotter and the some
average of that call based on information on all spotters. Adjust the
offset of the spotter by a small amount.

Show the spot with the adjusted frequency.  Add digits to the
frequency to add precision.

To adjust against drift of all spotters, for each spot, calculate how
much the frequency is adjusted and adjust by a small amount towards 0.


Validation

Output spotter offsets and examine the curves.

Define a metric on how "wrong" the frequencies are and compare it
against the non-complensated frequencies (for every spot).

Metric: For each spot, if the same call has been spotted recently
(last 10 minutes), sum the difference in the frequency since last
spot. Ignore big changes >0.3kHz. Different spotters may typically add
0.1 if there is a drift. Small QSYs <0.3kHz will be counted once. For
the adjusted frequencies, calculate the jumps in frequencies adjusted
by the offset of the spotter.

"""

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


if __name__ == "__main__":
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
