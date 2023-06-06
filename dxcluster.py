import re
import socket

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

class Spot(object):
    def __init__(self, spotter, freq, dx, mode, speed, t, time):
        self.spotter = spotter
        self.freq = freq
        self.dx = dx
        self.mode = mode
        self.speed = speed
        self.type = t
        self.time = time


def spots(call, address):
    """Yields spots from the DX cluster.
    CALL is the call given when logging in to the DX cluster.
    ADDRESS is given to socket.socket.connect
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(address)

        reader = Reader(s)
        print(reader.readline())
        s.sendall(call.encode() + b'\r\n')
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
                yield Spot(m.group(1), float(m.group(2)), m.group(4),
                           m.group(5), m.group(6), m.group(7), m.group(8))
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