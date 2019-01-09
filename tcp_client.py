import socket
import struct
import threading
import time
from select import select
from constants import *

ADAPTER_IP_ADDR = '127.0.0.1'
ADAPTER_TCP_PORT = 9999


class SendCANThd(threading.Thread):
    def __init__(self, conn):
        super(SendCANThd, self).__init__()
        self._stop_event = threading.Event()
        self._conn = conn

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        try:
            while not self.stopped():
                self._conn.send_frame(PACKET_TYPE_CAN_FRAME, 0x7ef, b'12345678')
                time.sleep(1)
        except Exception as e:
            print(e)
            pass
        finally:
            pass


class Connection:
    def __init__(self):
        self.sock = None
        self.send_thd = SendCANThd(self)
        self.send_lock = threading.Lock()
        self.read_buf = b''

    def connect(self):
        self.sock = socket.create_connection((ADAPTER_IP_ADDR, ADAPTER_TCP_PORT))
        self.sock.setblocking(0)
        self.send_thd.start()

    def close(self):
        self.send_thd.stop()
        self.send_thd.join()
        self.sock.close()
        self.read_buf = b''

    def send_all(self, data):
        amount_sent = 0
        while amount_sent < len(data):
            _, writables, _ = select([], [self.sock], [], 1)
            if len(writables) > 0:
                amount_sent += self.sock.send(data[amount_sent:])

    def receive_packet(self, on_packet_received, on_peer_shutdown):
        readables, _, _ = select([self.sock], [], [], 0.5)
        if len(readables) > 0:
            if len(self.read_buf) < SIZEOF_PACKET_HEADER:
                required_len = SIZEOF_PACKET_HEADER - len(self.read_buf)
            else:
                header = struct.unpack('>HH', self.read_buf[0:SIZEOF_PACKET_HEADER])
                if header[0] < SIZEOF_PACKET_HEADER:
                    raise RuntimeError("Invalid packet length: {}".format(header[0]))
                payload_length = header[0] - SIZEOF_PACKET_HEADER
                required_len = SIZEOF_PACKET_HEADER + payload_length - len(self.read_buf)
            recved = self.sock.recv(required_len)
            if not recved:
                on_peer_shutdown()
            else:
                self.read_buf += recved
                header = struct.unpack('>HH', self.read_buf[0:SIZEOF_PACKET_HEADER])
                payload_length = header[0] - SIZEOF_PACKET_HEADER
                if SIZEOF_PACKET_HEADER + payload_length == len(self.read_buf):
                    # tuple: (packet type, packet payload)
                    on_packet_received(header[1], self.read_buf[SIZEOF_PACKET_HEADER:])
                    self.read_buf = b''

    def send_packet(self, msg_type, packet_data):
        packet_data_len = len(packet_data)
        pkt = struct.pack('>HH', SIZEOF_PACKET_HEADER + packet_data_len, msg_type) + packet_data
        self.send_lock.acquire()
        self.send_all(pkt)
        self.send_lock.release()

    @staticmethod
    def parse_can_frame_packet(payload):
        if len(payload) <= SIZEOF_UINT16:
            raise RuntimeError("parse_fr_frame_packet, payload len error: {}".format(len(payload)))
        frame_payload_len = len(payload) - SIZEOF_UINT16
        t = struct.unpack('>H{}B'.format(frame_payload_len), payload)
        return t[0], t[1:]

    def send_frame(self, addr, payload):
        if len(payload) == 0:
            return 0
        print('Send:', hex(addr), payload)
        self.send_packet(PACKET_TYPE_CAN_FRAME, struct.pack('!I', addr) + payload)


if __name__ == "__main__":
    conn = Connection()
    conn.connect()

    def on_packet_recved(t, data):
        if t == PACKET_TYPE_CAN_FRAME:
            if len(data) <= 4:
                print('Invalid can frame packet:', len(data))
            addr = struct.unpack('!I', data[0:4])
            print('Recved:', hex(addr), data[4:])

    try:
        while True:
            conn.receive_packet(on_packet_recved, lambda: print('Disconnected'))
    except Exception as e:
        print(e)
