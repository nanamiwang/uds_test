from __future__ import print_function
import struct
import SocketServer
from select import select
import threading
from constants import *
from panda import Panda
from binascii import hexlify

CAN_BUS = 0x0

class RecvCANThd(threading.Thread):
    def __init__(self):
        super(RecvCANThd, self).__init__()
        self._stop_event = threading.Event()
        self.lock = threading.Lock()
        self.send_sock = None

    def set_send_sock(self, s):
        self.lock.acquire()
        self.send_sock = s
        self.lock.release()

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
        pkt = struct.pack('!HH', SIZEOF_PACKET_HEADER + packet_data_len, msg_type) + packet_data
        self.send_all(pkt)

    def run(self):
        try:
            while not self.stopped():
                messages = panda.can_recv()
                self.lock.acquire()
                if self.send_sock:
                    for rx_addr, rx_ts, rx_data, rx_bus in messages:
                        #print('Recved from panda:', hex(rx_addr), hexlify(rx_data))
                        self.send_packet(PACKET_TYPE_CAN_FRAME, struct.pack('!I', rx_addr) + rx_data)
                self.lock.release()
        except Exception as e:
            print(e)
            pass
        finally:
            pass


class TcpServerHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        print('Client connnected')
        read_buf = b''
        self.request.setblocking(0)
        recv_can_thd.set_send_sock(self.request)
        try:
            while True:
                readables, _, _ = select([self.request], [], [], 0.5)
                if len(readables) > 0:
                    if len(read_buf) < SIZEOF_PACKET_HEADER:
                        required_len = SIZEOF_PACKET_HEADER - len(read_buf)
                    else:
                        header = struct.unpack('!HH', read_buf[0:SIZEOF_PACKET_HEADER])
                        print("total len:", header[0], 'type:', header[1])
                        if header[0] < SIZEOF_PACKET_HEADER:
                            raise RuntimeError("Invalid packet length: {}".format(header[0]))
                        required_len = header[0] - len(read_buf)
                    recved = self.request.recv(required_len)
                    if not recved:
                        print("Client send FIN")
                        break
                    else:
                        read_buf += recved
                        if len(read_buf) < SIZEOF_PACKET_HEADER:
                            continue
                        header = struct.unpack('!HH', read_buf[0:SIZEOF_PACKET_HEADER])
                        if header[0] == len(read_buf):
                            print('Recved packet, len: {}:{}'.format(header[0]), hexlify(read_buf))
                            # tuple: (packet type, packet payload)
                            if header[1] == PACKET_TYPE_CAN_FRAME:
                                data = read_buf[SIZEOF_PACKET_HEADER:]
                                if len(data) <= 4:
                                    print('Invalid can frame packet:', len(data))
                                addr = struct.unpack('!I', data[0:4])
                                if len(addr) == 0:
                                    print('Invalid can frame packet data:', hexlify(data))
                                    break
                                print('Recved CAN frame from client:', hex(addr[0]), hexlify(data[4:]))
                                panda.can_send(addr[0], data[4:], CAN_BUS)
                            read_buf = b''
        except Exception as e:
            print(e)
        finally:
            recv_can_thd.set_send_sock(None)


class ServerThd(threading.Thread):
    def __init__(self, server):
        super(ServerThd, self).__init__()
        self._server = server

    def run(self):
        print('Listening...')
        self._server.serve_forever()

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
    HOST, PORT = "0.0.0.0", 9999
    tcp_server = SocketServer.TCPServer((HOST, PORT), TcpServerHandler)
    ServerThd(tcp_server).start()
    while True:
        text = raw_input("Press q to exit")
        if text == 'q':
            break
    tcp_server.shutdown()
    print('Exiting...')
    recv_can_thd.stop()
    recv_can_thd.join()
