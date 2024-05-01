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

import csv
import math
import re
import socket
import statistics
import time

import dxcluster

HOST = 'rbn.telegraphy.de'    # The remote host
PORT = 7000              # The same port as used by the server
CALL = 'SM5OUU'

QSY_MIN_DISTANCE = 1.0

class SpotAverage(object):
    """Keep the average of a certain spot"""
    def __init__(self, dx):
        self.dx = dx
        self.spotters = dict()

    def adjust(self, spotter, freq):
        if spotter in self.spotters:
            offset = freq - self.spotters[spotter]
            if abs(offset) > 0.05:
                # QSY detected if one spotter moves it
                self.spotters = dict()
                print(self.dx, "qsy", offset)
        if len(self.spotters) > 0:
            offset = freq - statistics.mean(self.spotters.values())
            if abs(offset) > QSY_MIN_DISTANCE:
                # QSY detected by new spotter
                self.spotters = dict()
                print(self.dx, "qsy on new spotter", offset)
        self.spotters[spotter] = freq
        return statistics.mean(self.spotters.values())

def calc_band(freq):
    if freq < 2000:
        return "160m"
    if freq < 4000:
        return "80m"
    if freq < 7500:
        return "40m"
    if freq < 11000:
        return "30m"
    if freq < 15000:
        return "20m"
    if freq < 19000:
        return "17m"
    if freq < 22000:
        return "15m"
    if freq < 25000:
        return "12m"
    if freq < 30000:
        return "10m"
    if freq < 52000:
        return "6m"
    return "OTHER"

def top_adjustments(d):
    return sorted([(abs(adj), val, adj) for val,adj in d.items()],
                  reverse=True)[:3]


class Trace(object):
    """Remember log information and output it to a csv file."""
    def __init__(self, filename):
        self.filename = filename
        self.rows = []
        self.last_time = int(time.time())
        self.dict = {}
        self.count_fieldnames = {}

    def _flush(self):
        if self.dict:
            self.dict["when"] = self.last_time
            self.rows.append(self.dict)
            self.dict = {}
        
    def trace(self, call, entry):
        if call not in self.count_fieldnames:
            self.count_fieldnames[call] = 0
        self.count_fieldnames[call] = self.count_fieldnames[call] + 1
        now = int(time.time())
        if now != self.last_time:
            self._flush()
            self.last_time = now
        self.dict[call] = entry
        return

    def dump(self):
        self._flush()
        with open(self.filename + ".csv", "w") as csvfile:
            writer = csv.DictWriter(csvfile,
                                    fieldnames=["when"] +
                                    [call for call, entry
                                     in sorted(self.count_fieldnames.items(),
                                               key=lambda x: x[1],
                                               reverse=True)])
            writer.writeheader()
            for row in self.rows:
                writer.writerow(row)


if __name__ == "__main__":
    trace_spotters = {}
    trace_dxes = {}
    try:
        count = 0
        dxes = dict() # (call, band) => SpotAverage
        spotter_adjustments = dict() # (str, band) => float
        total = 0
        for spot in dxcluster.spots(CALL, (HOST, PORT)):
            count = count + 1
            if count % 100 == 0:
                print(count, "spots filtered", "total", len(dxes), "monitored")
                print(top_adjustments(spotter_adjustments))
                print("total drift:", total)
            band = calc_band(spot.freq)
            spotter_band = (spot.spotter, band)
            if spotter_band not in spotter_adjustments:
                spotter_adjustments[spotter_band] = 0.0
            adjusted_frequency_1 = spot.freq + spotter_adjustments[spotter_band]
            index = (spot.dx, band)
            if index not in dxes:
                dxes[index] = SpotAverage(spot.dx)
            adjusted_frequency_2 = dxes[index].adjust(spot.spotter, adjusted_frequency_1)
            spotout = spot.spotter + ":"
            print(f"DX de {spotout:<15s}",
                  f"{adjusted_frequency_2:>9.3f}",
                  f"{spot.dx:<14}", spot.rest)

            # Adjust the spotter
            spotted_freq_diff = adjusted_frequency_2 - adjusted_frequency_1
            spotter_adjustments[spotter_band] += spotted_freq_diff / 10

            total_freq_diff = adjusted_frequency_2 - spot.freq
            total += total_freq_diff
            correction = total * total * total / 1000
            if abs(correction) < QSY_MIN_DISTANCE:
                spotter_adjustments[spotter_band] -= correction
            total -= total / 10

            if band not in trace_spotters:
                trace_spotters[band] = Trace("spotters" + band)
            trace_spotters[band].trace(" ".join(spotter_band),
                                       spotter_adjustments[spotter_band])
            if band not in trace_dxes:
                trace_dxes[band] = Trace("dxes" + band)
            trace_dxes[band].trace(spot.dx, adjusted_frequency_2)
    finally:
        for v in trace_spotters.values():
            v.dump()
        for v in trace_dxes.values():
            v.dump()
