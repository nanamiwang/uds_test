from __future__ import print_function
import struct
import sys
from panda import Panda
from binascii import hexlify, unhexlify
from time import sleep

CAN_BUS = 0x0

if __name__ == "__main__":
    try:
        panda = Panda()
        # allow all output
        panda.set_safety_mode(0x1337)
        # clear tx buffer
        panda.can_clear(0x0)
        # clear rx buffer
        panda.can_clear(0xFFFF)

        data = unhexlify(b'10082324F0010098')
        addr = 0x0
        for i in range(0x800):
            print('Try', hex(addr + i))
            panda.can_send(addr + i, data, CAN_BUS)
            sleep(0.1)
            for _ in range(100):
                messages = panda.can_recv()
                for rx_addr, rx_ts, rx_data, rx_bus in messages:
                    if rx_data[0:1] == unhexlify(b'30'):
                        print('Found addr', hex(addr + i))
                        sys.exit(0)
    except Exception as e:
        print(e)
