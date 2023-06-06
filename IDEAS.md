# Frequency-adjusting filter

I have noticed that sometimes the same spot shows up with different
frequencies.  Is this because the spotters are varying a little in
frequency.  If so, it should be possible to calculate how much each
spotter deviates from the others and then adjust each spot's frequency
based on that.

## Important verification
That the program can use more precise frequencies.

## Logic
Each spotter has an offset per band.

To adjust the spotter offset, for each spot, calculate the difference
between the spotter's offset frequency and the the floating average of
that call for the last five minutes. Adjust the offset by a small
amount.

Show the spot with the adjusted frequency.  Add one digit.

To adjust against drift, for each spot, calculate how much the
frequency is adjusted and adjust by a small amount towards 0.

## Validation

Define a metric on how "wrong" the frequencies are and compare it
against the non-complensated frequencies (for every spot).

Metric: For each spot, if the same call has been spotted recently
(last 10 minutes), sum the difference in the frequency since last
spot. Ignore big changes >0.3kHz. Different spotters may typically add
0.1 if there is a drift. Small QSYs <0.3kHz will be counted once. For
the adjusted frequencies, calculate the jumps in frequencies adjusted
by the offset of the spotter.

