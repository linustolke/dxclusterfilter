import pywsjtx
import re
import socket

import spot

UDP_IP = "127.0.0.1"
UDP_PORT = 2237

def add_argument(parser):
    parser.add_argument("--ft8", action='store_true', default=False,
                        help='Fetch data from FT8')

def spots():
    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))

    counter = 0
    de_call = ""
    freq = 0
    mode = ""
    while True:
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        packet = pywsjtx.WSJTXPacketClassFactory.from_udp_packet(addr, data)
        if packet.TYPE_VALUE == 0:
            # Heartbeat
            counter += 1
            if counter % 10 == 0:
                print("FT8 10 HB")
            continue
        if packet.TYPE_VALUE == 1:
            # Status
            de_call = packet.de_call
            freq = packet.dial_frequency / 1000
            mode = packet.mode
            continue
        if packet.TYPE_VALUE == 2:
            # Decode Packet
            m = re.match(r"<?(CQ [A-Z][A-Z]|[^ >]+)>? <?([^ >]+)>?( ([A-Z][A-Z][0-9][0-9]))?",
                         packet.message)
            if m:
                when = "{0:02d}{1:02d}".format(packet.time.hour, packet.time.minute)
                word1 = m.group(1)
                word2 = m.group(2)
                word3 = m.group(4)
                if word1 == "CQ":
                    type = "CQ"
                elif word3 in ["73", "RR73"]:
                    type = "73"
                else:
                    type = "QSO"
                yield spot.Spot(de_call,
                                freq,
                                m.group(2),
                                mode,
                                "", # Speed unit
                                type, # Type
                                when, # Time
                                "") # Rest
            else:
                print("FT8: Not parsed:", packet.message)

        elif packet.TYPE_VALUE in [
                3, # Clear
                5, # QSOLogged
                6, # Close
                8, # HaltTx
        ]:
            # Packet type ignored
            pass
        else:
            print("FT8 received unknown packet:", packet)

def add(args):
    if args.ft8:
        return [spots()]
    else:
        return []

