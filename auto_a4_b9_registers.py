ERAY_PRTC1 = 0x084C000A
ERAY_PRTC2 = 0x3CB41212
ERAY_MHDC = 0x003F0006
ERAY_SUCC1 = 0x05400000
ERAY_GTUC01 = 0x00009C40
ERAY_GTUC02 = 0x000403E8
ERAY_GTUC03 = 0x000A1919
ERAY_GTUC04 = 0x0393038E
ERAY_GTUC05 = 0x34010404
ERAY_GTUC06 = 0x00310081
ERAY_GTUC07 = 0x000C0032
ERAY_GTUC08 = 0x004B0004
ERAY_GTUC09 = 0x00010308
ERAY_GTUC10 = 0x00D20032
ERAY_GTUC11 = 0
ERAY_SUCC2 = 0x0F0272E2
ERAY_SUCC3 = 0x000000EA
ERAY_NEMC = 0x00000008


def extract_bits(val, highest, lowest):
    return (val >> lowest) & ((1 << (highest - lowest + 1)) - 1)


def decode_flexray_params():
    params = dict()
    params['gdTSSTransmitter'] = extract_bits(ERAY_PRTC1, 3, 0)
    params['gdCASRxLowMax'] = extract_bits(ERAY_PRTC1 | (1 << 10), 10, 4)
    # 0 for 10M, 1 for 5M, 2 for 2.5M
    params['BIT_RATE'] = extract_bits(ERAY_PRTC1, 15, 14)
    params['gdWakeupSymbolRxWindow'] = extract_bits(ERAY_PRTC1, 24, 16)
    params['pWakeupPattern'] = extract_bits(ERAY_PRTC1, 31, 26)

    params['gdWakeupSymbolRxIdle'] = extract_bits(ERAY_PRTC2, 5, 0)
    params['gdWakeupSymbolRxLow'] = extract_bits(ERAY_PRTC1, 13, 8)
    params['pWakeupPattern'] = extract_bits(ERAY_PRTC1, 31, 26)
    params['pWakeupPattern'] = extract_bits(ERAY_PRTC1, 31, 26)
    params['pWakeupPattern'] = extract_bits(ERAY_PRTC1, 31, 26)
    return params


if __name__ == "__main__":
    d = decode_flexray_params()
    for k in d.keys():
        print(k, d[k])