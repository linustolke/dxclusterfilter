class Spot(object):
    """This is a spot as returned from spots.

    The fields of the class are:
    spotter - the call of the spotter
    frequency (a float)
    dx - the call spotted
    mode - the mode
    speed_unit - the unit of the speed, either WPM or BD
    type - the type of the spot, CQ, BEACON, ...
    time - the time of the spot. Four digits and a Z
    time - the rest of the line, everything except spotter, freq, and dx
    """

    def __init__(self, spotter, freq, dx, mode, speed_unit, t, time, rest):
        self.spotter = spotter
        self.freq = freq
        self.dx = dx
        self.mode = mode
        self.speed_unit = speed_unit
        self.type = t
        self.time = time
        self.rest = rest


