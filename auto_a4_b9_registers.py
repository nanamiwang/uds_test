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
    params['gdWakeupSymbolTxIdle'] = extract_bits(ERAY_PRTC1, 23, 16)
    params['gdWakeupSymbolTxLow'] = extract_bits(ERAY_PRTC1, 29, 24)

    params['gPayloadLengthStatic'] = extract_bits(ERAY_MHDC, 6, 0)
    params['pLatestTx'] = extract_bits(ERAY_MHDC, 28, 16)

    params['pWakeupChannel'] = extract_bits(ERAY_SUCC1, 21, 21)
    params['pAllowPassiveToActive'] = extract_bits(ERAY_SUCC1, 20, 16)
    params['gColdStartAttempts'] = extract_bits(ERAY_SUCC1, 15, 11)
    params['pKeySlotUsedForSync'] = extract_bits(ERAY_SUCC1, 9, 9)
    params['pKeySlotUsedForStartup'] = extract_bits(ERAY_SUCC1, 8, 8)
    params['pAllowHaltDueToClock'] = extract_bits(ERAY_SUCC1, 23, 23)
    a = extract_bits(ERAY_SUCC1, 26, 26)
    b = extract_bits(ERAY_SUCC1, 27, 27)
    if a == 1 and b == 1:
        params['pChannels'] = 2
    elif a == 1:
        params['pChannels'] = 0
    elif b == 1:
        params['pChannels'] = 1

    params['pMicroPerCycle'] = extract_bits(ERAY_GTUC01, 19, 0)

    params['gMacroPerCycle'] = extract_bits(ERAY_GTUC02, 13, 0)
    params['gSyncNodeMax'] = extract_bits(ERAY_GTUC02, 19, 16)

    params['pMicroInitialOffsetA'] = extract_bits(ERAY_GTUC03, 7, 0)
    params['pMicroInitialOffsetB'] = extract_bits(ERAY_GTUC03, 15, 8)
    params['gMacroInitialOffsetA'] = extract_bits(ERAY_GTUC03, 22, 16)
    params['gMacroInitialOffsetB'] = extract_bits(ERAY_GTUC03, 30, 24)

    params['gdNIT'] = params['gMacroPerCycle'] - extract_bits(ERAY_GTUC04, 13, 0) - 1
    params['gOffsetCorrectionStart'] = extract_bits(ERAY_GTUC04, 29, 16) + 1

    params['pDelayCompensationA'] = extract_bits(ERAY_GTUC05, 7, 0)
    params['pDelayCompensationB'] = extract_bits(ERAY_GTUC05, 15, 8)
    params['pClusterDriftDamping'] = extract_bits(ERAY_GTUC05, 20, 16)
    params['pDecodingCorrection'] = extract_bits(ERAY_GTUC05, 31, 24)

    params['pdAcceptedStartupRange'] = extract_bits(ERAY_GTUC06, 10, 0)
    params['pdMaxDrift'] = extract_bits(ERAY_GTUC06, 26, 16)

    params['gdStaticSlot'] = extract_bits(ERAY_GTUC07, 9, 0)
    params['gNumberOfStaticSlots'] = extract_bits(ERAY_GTUC07, 25, 16)

    params['gdMinislot'] = extract_bits(ERAY_GTUC08, 5, 0)
    params['gNumberOfMinislots'] = extract_bits(ERAY_GTUC08, 28, 16)

    params['gdActionPointOffset'] = extract_bits(ERAY_GTUC09, 5, 0)
    params['gdMinislotActionPointOffset'] = extract_bits(ERAY_GTUC09, 12, 8)
    params['gdDynamicSlotIdlePhase'] = extract_bits(ERAY_GTUC09, 17, 16)

    params['pOffsetCorrectionOut'] = extract_bits(ERAY_GTUC10, 13, 0)
    params['pRateCorrectionOut'] = extract_bits(ERAY_GTUC10, 26, 16)

    params['pdListenTimeout'] = extract_bits(ERAY_SUCC2, 20, 0)
    params['gListenNoise'] = extract_bits(ERAY_SUCC2, 27, 24) + 1

    params['gMaxWithoutClockCorrectionPassive'] = extract_bits(ERAY_SUCC3, 3, 0)
    params['gMaxWithoutClockCorrectionFatal'] = extract_bits(ERAY_SUCC3, 7, 4)

    params['gNetworkManagementVectorLength'] = extract_bits(ERAY_NEMC, 3, 0)

    return params


if __name__ == "__main__":
    d = decode_flexray_params()
    for k in d.keys():
        print(k, d[k])