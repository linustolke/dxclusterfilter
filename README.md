# dxclusterfilter

This is some tools used to process the output from the reverse beacon
network for some specific purposes.

These scripts are not very mature even though occationally used by the
author. Consider them as inspiration for future work.

Author: Linus Tolke, SM5OUU

## filter_ships.py

Shows only certain spots with added information from another source.

Used during Museum Ships weekend and [International Lighthouse Lightship Weekend](https://illw.net/) to get info when ships are calling CQ.

The ships for the Museum ships weekend 2023 are in `ships.csv`, or give the ship name with `--file=file.csv`.

For the [International Lighthouse Lightship
Weekend](https://illw.net/) 2023 this was improved with a possibility
to get the information from the web page directly using the command
`--url https://illw.net/index.php/entrants-list-2023`.

For 2024, a possibility to monitor and filter FT8 received by wsjtx running on the same host.

## frequency_adjuster.py

The reverse beacon network only delivers the frequency with a 100Hz
precision.  Assuming that each skimmer is stable in frequency and that
some of them has an offset to the correct frequency, observing
multiple skimmers and how they report multiple spotted stations, the
frequency offset of the skimmers can be calculated and the frequency
of the spots can be adjusted.

Whether this works in practice remains to be tested.

<!-- Local Variables:             -->
<!-- eval:(visual-line-mode 1)    -->
<!-- End:                         -->
