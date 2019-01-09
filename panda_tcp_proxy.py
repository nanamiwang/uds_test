from __future__ import print_function
import struct
import socketserver
from select import select
import threading
from constants import *
from panda import Panda

CAN_BUS = 0x0

class RecvCANThd(threading.Thread):
    def __init__(self, p):
        super(RecvCANThd, self).__init__()
        self._stop_event = threading.Event()
        self.lock = threading.Lock()
        self.send_sock = None

    def set_send_sock(self, s):
        self.send_lock.acquire()
        self.send_sock = s
        self.send_lock.release()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def send_all(self, data):
        amount_sent = 0
        while amount_sent < len(data):
            _, writables, _ = select([], [self.send_sock], [], 1)
            if len(writables) > 0:
                amount_sent += self.send_sock.send(data[amount_sent:])

    def send_packet(self, msg_type, packet_data):
        packet_data_len = len(packet_data)
        pkt = struct.pack('>HH', SIZEOF_PACKET_HEADER + packet_data_len, msg_type) + packet_data
        self.send_lock.acquire()
        self.send_all(pkt)
        self.send_lock.release()

    def run(self):
        try:
            while not self.stopped():
                messages = panda.can_recv()
                self.lock.acquire()
                if self.send_sock:
                    for rx_addr, rx_ts, rx_data, rx_bus in messages:
                        self.send_packet(PACKET_TYPE_CAN_FRAME, struct.pack('!I', rx_addr) + rx_data)
                self.lock.release()
        except Exception as e:
            print(e)
            pass
        finally:
            pass


class TcpServerHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.read_buf = b''
        self.request.setblocking(0)
        while True:
            try:
                readables, _, _ = select([self.request], [], [], 0.5)
                if len(readables) > 0:
                    if len(self.read_buf) < SIZEOF_PACKET_HEADER:
                        required_len = SIZEOF_PACKET_HEADER - len(self.read_buf)
                    else:
                        header = struct.unpack('>HH', self.read_buf[0:SIZEOF_PACKET_HEADER])
                        if header[0] < SIZEOF_PACKET_HEADER:
                            raise RuntimeError("Invalid packet length: {}".format(header[0]))
                        payload_length = header[0] - SIZEOF_PACKET_HEADER
                        required_len = SIZEOF_PACKET_HEADER + payload_length - len(self.read_buf)
                    recved = self.request.recv(required_len)
                    if not recved:
                        break
                    else:
                        self.read_buf += recved
                        header = struct.unpack('>HH', self.read_buf[0:SIZEOF_PACKET_HEADER])
                        payload_length = header[0] - SIZEOF_PACKET_HEADER
                        if SIZEOF_PACKET_HEADER + payload_length == len(self.read_buf):
                            # tuple: (packet type, packet payload)
                            if header[1] == PACKET_TYPE_CAN_FRAME:
                                data = self.read_buf[SIZEOF_PACKET_HEADER:]
                                if len(data) <= 4:
                                    print('Invalid can frame packet:', len(data))
                                addr = struct.unpack('!I', data[0:4])
                                panda.can_send(addr, self.read_buf[SIZEOF_PACKET_HEADER:], CAN_BUS)
                            self.read_buf = b''
            except Exception as e:
                print(e)
                break


if __name__ == "__main__":
    panda = Panda()
    # allow all output
    panda.set_safety_mode(0x1337)
    # clear tx buffer
    panda.can_clear(0x0)
    # clear rx buffer
    panda.can_clear(0xFFFF)

    recv_can_thd = RecvCANThd()
    recv_can_thd.start()
    HOST, PORT = "localhost", 9999
    tcp_server = socketserver.TCPServer((HOST, PORT), TcpServerHandler)

    # Activate the TCP server.
    # To abort the TCP server, press Ctrl-C.
    tcp_server.serve_forever()