import yaml

# 0xF0010090
ERAY_PRTC1 = 0x084C000A
# 0xF0010094
ERAY_PRTC2 = 0x3CB41212
# 0xF0010098
ERAY_MHDC = 0x003F0006
# 0xF0010080
ERAY_SUCC1 = 0x05400000
# # 0xF00100A0
ERAY_GTUC01 = 0x00009C40
# # 0xF00100A4
ERAY_GTUC02 = 0x000403E8
# # 0xF00100A8
ERAY_GTUC03 = 0x000A1919
# # 0xF00100AC
ERAY_GTUC04 = 0x0393038E
# # 0xF00100B0
ERAY_GTUC05 = 0x34010404
# # 0xF00100B4
ERAY_GTUC06 = 0x00310081
# # 0xF00100B8
ERAY_GTUC07 = 0x000C0032
# # 0xF00100BC
ERAY_GTUC08 = 0x004B0004
# # 0xF00100C0
ERAY_GTUC09 = 0x00010308
# # 0xF00100C4
ERAY_GTUC10 = 0x00D20032
# 0xF0010084
ERAY_SUCC2 = 0x0F0272E2
# 0xF0010088
ERAY_SUCC3 = 0x000000EA
ERAY_NEMC = 0x00000008
ERAY_WRHS1 = 0x35000003


cClockDeviationMax = 0.0015


def extract_bits(val, highest, lowest):
    return (val >> lowest) & ((1 << (highest - lowest + 1)) - 1)


def decode_flexray_config():
    config = dict({
        'nStar': 0,
        'LineLength': 12,
        'pdBDTx': 0.0,
        'pdBDRx': 0.0,
        'pdStarDelay': 0.25,
        'gdMinPropagationDelay': 0.0,
        'pKeySlotOnlyEnabled': 0,
        'pPayloadLengthDynMax': 127,
        'CLOCK_SRC': 0,
        'SCM_EN': 0,
        'LOG_STATUS_DATA': 1,
        'FIFOA_EN': 0,
        'FIFOA_Depth': 0,
        'FIFOA_MIAFV': 0,
        'FIFOA_MIAFM': 0,
        'FIFOA_F0_EN': 0,
        'FIFOA_F0_MODE': 0,
        'FIFOA_F0_SID_LOWER': 0,
        'FIFOA_F0_SID_UPPER': 0,
        'FIFOA_F1_EN': 0,
        'FIFOA_F1_MODE': 0,
        'FIFOA_F1_SID_LOWER': 0,
        'FIFOA_F1_SID_UPPER': 0,
        'FIFOA_F2_EN': 0,
        'FIFOA_F2_MODE': 0,
        'FIFOA_F2_SID_LOWER': 0,
        'FIFOA_F2_SID_UPPER': 0,
        'FIFOA_F3_EN': 0,
        'FIFOA_F3_MODE': 0,
        'FIFOA_F3_SID_LOWER': 0,
        'FIFOA_F3_SID_UPPER': 0,
        'FIFOB_EN': 0,          # Receive FIFO for channel B enabled
        'FIFOB_Depth': 0,
        'FIFOB_MIAFV': 0,
        'FIFOB_MIAFM': 0,
        'FIFOB_F0_EN': 0,
        'FIFOB_F0_MODE': 0,
        'FIFOB_F0_SID_LOWER': 0,
        'FIFOB_F0_SID_UPPER': 0,
        'FIFOB_F1_EN': 0,
        'FIFOB_F1_MODE': 0,
        'FIFOB_F1_SID_LOWER': 0,
        'FIFOB_F1_SID_UPPER': 0,
        'FIFOB_F2_EN': 0,
        'FIFOB_F2_MODE': 0,
        'FIFOB_F2_SID_LOWER': 0,
        'FIFOB_F2_SID_UPPER': 0,
        'FIFOB_F3_EN': 0,
        'FIFOB_F3_MODE': 0,
        'FIFOB_F3_SID_LOWER': 0,
        'FIFOB_F3_SID_UPPER': 0,
        'RxMsgBufs': [                  # Receive frames configuration
            {
                'FrameId': 1,           # The slot id we are listening on
                'Channels': 1,          # The channel we are listening on
                'CCF_EN': 0,            # Cycle counter filter enabled
                'CCF_VAL': 0,           # Cycle counter filter value
                'CCF_MASK': 0,          # Cycle counter filter mask
            },
        ],
        'TxMsgBufs': [  # Transmit frames configuration
            {
                'FrameId': 3,  # The id of the slot which frame will be send on
                'PayloadLenMax': 8,  # Max payload length in words, for dynamic slot and DynPayloadLen=1 only
                'Channels': 1,  # The channel which frame will be send to
                'CCF_EN': 0,  # Cycle counter filter enabled
                'CCF_VAL': 0,  # Cycle counter filter value
                'CCF_MASK': 0,  # Cycle counter filter mask
                'DynPayloadLen': 0,  # Dynamic payload length enabled, for dynamic slot only
                'PPI': 0,  # Payload preempt flag
            },
        ]
    })
    config['gdTSSTransmitter'] = extract_bits(ERAY_PRTC1, 3, 0)
    config['gdCasRxLowMax'] = extract_bits(ERAY_PRTC1 | (1 << 10), 10, 4)
    # 0 for 10M, 1 for 5M, 2 for 2.5M
    config['BIT_RATE'] = extract_bits(ERAY_PRTC1, 15, 14)
    pdMicrotick_values = [25.0, 25.0, 50.0]
    pdMicrotick = pdMicrotick_values[config['BIT_RATE']] / 1000.0
    print('pdMicrotick', pdMicrotick)
    config['gdWakeupRxWindow'] = extract_bits(ERAY_PRTC1, 24, 16)
    config['pWakeupPattern'] = extract_bits(ERAY_PRTC1, 31, 26)

    config['gdWakeupSymbolRxIdle'] = extract_bits(ERAY_PRTC2, 5, 0)
    config['gdWakeupSymbolRxLow'] = extract_bits(ERAY_PRTC2, 13, 8)
    config['gdWakeupSymbolTxIdle'] = extract_bits(ERAY_PRTC2, 23, 16)
    config['gdWakeupSymbolTxActive'] = extract_bits(ERAY_PRTC2, 29, 24)

    config['gPayloadLengthStatic'] = extract_bits(ERAY_MHDC, 6, 0)
    config['pLatestTx'] = extract_bits(ERAY_MHDC, 28, 16)

    config['pWakeupChannel'] = extract_bits(ERAY_SUCC1, 21, 21)
    config['pAllowPassiveToActive'] = extract_bits(ERAY_SUCC1, 20, 16)
    config['gColdStartAttempts'] = extract_bits(ERAY_SUCC1, 15, 11)
    config['pKeySlotUsedForSync'] = extract_bits(ERAY_SUCC1, 9, 9)
    config['pKeySlotUsedForStartup'] = extract_bits(ERAY_SUCC1, 8, 8)
    config['pAllowHaltDueToClock'] = extract_bits(ERAY_SUCC1, 23, 23)
    a = extract_bits(ERAY_SUCC1, 26, 26)
    b = extract_bits(ERAY_SUCC1, 27, 27)
    if a == 1 and b == 1:
        config['pChannels'] = 2
    elif a == 1:
        config['pChannels'] = 0
    elif b == 1:
        config['pChannels'] = 1

    config['pMicroPerCycle'] = extract_bits(ERAY_GTUC01, 19, 0)

    gMacroPerCycle = extract_bits(ERAY_GTUC02, 13, 0)
    config['gdMacrotick'] = config['pMicroPerCycle'] // gMacroPerCycle * pdMicrotick
    # gSyncNodeMax replaced by gSyncFrameIDCountMax in spec 3.1
    config['gSyncFrameIDCountMax'] = extract_bits(ERAY_GTUC02, 19, 16)

    config['pMicroInitialOffsetA'] = extract_bits(ERAY_GTUC03, 7, 0)
    config['pMicroInitialOffsetB'] = extract_bits(ERAY_GTUC03, 15, 8)
    config['pMacroInitialOffsetA'] = extract_bits(ERAY_GTUC03, 22, 16)
    config['pMacroInitialOffsetB'] = extract_bits(ERAY_GTUC03, 30, 24)

    config['gdNIT'] = gMacroPerCycle - extract_bits(ERAY_GTUC04, 13, 0) - 1
    config['gOffsetCorrectionStart'] = extract_bits(ERAY_GTUC04, 29, 16) + 1

    config['pDelayCompensationA'] = extract_bits(ERAY_GTUC05, 7, 0)
    config['pDelayCompensationB'] = extract_bits(ERAY_GTUC05, 15, 8)
    config['pClusterDriftDamping'] = extract_bits(ERAY_GTUC05, 20, 16)
    config['pDecodingCorrection'] = extract_bits(ERAY_GTUC05, 31, 24)

    config['pdAcceptedStartupRange'] = extract_bits(ERAY_GTUC06, 10, 0)
    config['pdMaxDrift'] = extract_bits(ERAY_GTUC06, 26, 16)

    config['gdStaticSlot'] = extract_bits(ERAY_GTUC07, 9, 0)
    config['gNumberOfStaticSlots'] = extract_bits(ERAY_GTUC07, 25, 16)

    config['gdMinislot'] = extract_bits(ERAY_GTUC08, 5, 0)
    config['gNumberOfMinislots'] = extract_bits(ERAY_GTUC08, 28, 16)

    config['gdActionPointOffset'] = extract_bits(ERAY_GTUC09, 5, 0)
    config['gdMiniSlotActionPointOffset'] = extract_bits(ERAY_GTUC09, 12, 8)
    config['gdDynamicSlotIdlePhase'] = extract_bits(ERAY_GTUC09, 17, 16)

    config['pOffsetCorrectionOut'] = extract_bits(ERAY_GTUC10, 13, 0)
    config['pRateCorrectionOut'] = extract_bits(ERAY_GTUC10, 26, 16)

    config['pdListenTimeout'] = extract_bits(ERAY_SUCC2, 20, 0)
    config['gListenNoise'] = extract_bits(ERAY_SUCC2, 27, 24) + 1

    config['gMaxWithoutClockCorrectionPassive'] = extract_bits(ERAY_SUCC3, 3, 0)
    config['gMaxWithoutClockCorrectionFatal'] = extract_bits(ERAY_SUCC3, 7, 4)

    config['gNetworkManagementVectorLength'] = extract_bits(ERAY_NEMC, 3, 0)

    config['pKeySlotId'] = extract_bits(ERAY_WRHS1, 10, 0)

    if (config['gdActionPointOffset'] <= config['gdMiniSlotActionPointOffset'] or config['gNumberOfMinislots'] == 0):
        adActionPointDifference = 0
    else:
        adActionPointDifference = config['gdActionPointOffset'] - config['gdMiniSlotActionPointOffset']
    # Constraint 18:
    config['gdSymbolWindow'] = gMacroPerCycle - (
            config['gdStaticSlot'] * config['gNumberOfStaticSlots'] + adActionPointDifference + config['gdMinislot'] * config['gNumberOfMinislots'] + config['gdNIT'])

    # Constraint 25
    config['gOffsetCorrectionMax'] = config['pOffsetCorrectionOut'] * (pdMicrotick * (1 - cClockDeviationMax))
    T0 = 0.01
    gdMaxPropagationDelay = config['pdBDTx'] + config['LineLength'] * T0 + config['pdStarDelay'] * config['nStar'] + config['pdBDRx']
    gdMaxMicrotick = pdMicrotick
    gAssumedPrecision = (34 + 20 * config['pClusterDriftDamping']) * gdMaxMicrotick + 2 * gdMaxPropagationDelay
    config['gdMaxInitializationError'] = gAssumedPrecision
    return config


if __name__ == "__main__":
    d = decode_flexray_config()
    for k in d.keys():
        print(k, d[k])
    with open('./audi_a4_b9.yml', 'w') as outfile:
        yaml.dump(d, outfile)
