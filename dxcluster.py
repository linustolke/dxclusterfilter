"""Methods for getting information from DX-cluster.

Currently only tested with rbn.telegraphy.de 7000 (i.e. the Reverse
Beacon Network)

"""

import re
import socket

import spot

class _Reader(object):
    def __init__(self, stream):
        self.buffer = b''
        self.stream = stream

    def readline(self):
        while True:
            end_of_line = self.buffer.find(b'\n')
            saved_buffer = self.buffer
            if end_of_line >= 0:
                first_line = self.buffer[0:end_of_line]
                self.buffer = self.buffer[end_of_line + 1:]
                try:
                    return first_line.decode()
                except UnicodeDecodeError as e:
                    print('Error decoding', saved_buffer)
                    raise
            chunk = self.stream.recv(2048)
            if not chunk:
                return None
            self.buffer += chunk

    def readsomething(self):
        if self.buffer:
            buf = self.buffer
            self.buffer = b''
            return buf.decode()
        return self.stream.recv(100).decode()


def spots(call, address):
    """Yields spots from the DX cluster.

    Arguments:
    The call given when logging in to the DX cluster.
    The address is given to socket.socket.connect
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print('Connecting to', address)
        s.connect(address)

        reader = _Reader(s)
        print(address, reader.readsomething())
        s.sendall(call.encode() + b'\r\n')
        print(address, reader.readline())
        s.sendall(b'set/raw\r\n')
        print(address, reader.readsomething())
        s.sendall(b'unset/wcy\r\n')
        print(address, reader.readsomething())
        s.sendall(b'unset/wwv\r\n')
        print(address, reader.readsomething())
        s.sendall(b'unset/wx\r\n')
        print(address, reader.readsomething())
        count = 0
        try:
            while True:
                data = reader.readline().strip()
                if data is None:
                    break
                count = count + 1
                if count % 1000 == 0:
                    print(address, count, "spots filtered")
                    # Contents matchers don't match whitespace
                REGEXP = (r"DX de ([^: ]*):\s+"         # 1 spotter
                          + r"([0-9]+(.[0-9]+)?)\s+"    # 3 frequency
                          + r"([^ ]+)\s+"               # 4 DX
                          + r"(.*)$")                   # 5 Rest
                m = re.match(REGEXP, data)
                if m:
                    rest = m.group(5)

                    m_mode = re.search(r"(CW|PSK31|PSK63|RTTY)\s", rest)
                    m_speed = re.search(r"[1-9][0-9]*\s+(WPM|BPS)\s", rest)
                    m_type = re.search(r"\s(BEACON|CQ|DX|NCDXF B)\s", rest)
                    m_time = re.search(r"\s([0-9]*Z)", rest)
                    yield spot.Spot(m.group(1),
                                    float(m.group(2)),
                                    m.group(4),
                                    m_mode.group(1) if m_mode else "",
                                    m_speed.group(1) if m_speed else "",
                                    m_type.group(1) if m_type else "",
                                    m_time.group(1) if m_time else "",
                                    m.group(5).strip())
                else:
                    print(address, "Not parsed", data, "using", REGEXP)
        finally:
            s.sendall(b'QUIT\r\n')
