import ctypes
import numpy as np
from picosdk.ps5000a import ps5000a as ps
import matplotlib.pyplot as plt
from picosdk.functions import adc2mV, assert_pico_ok
import time

enabled = 1
disabled = 0
analogue_offset = 0.0
def readChA(status,chandle):
    # Set up channel A
    # handle = chandle
    # channel = PS5000A_CHANNEL_A = 0
    # enabled = 1
    # coupling type = PS5000A_DC = 1
    # range = PS5000A_2V = 7
    # analogue offset = 0 V
    channel_range = ps.PS5000A_RANGE['PS5000A_2V']
    status["setChA"] = ps.ps5000aSetChannel(chandle,
                                            ps.PS5000A_CHANNEL['PS5000A_CHANNEL_A'],
                                            enabled,
                                            ps.PS5000A_COUPLING['PS5000A_DC'],
                                            channel_range,
                                            analogue_offset)
    assert_pico_ok(status["setChA"])

    # Size of capture
    sizeOfOneBuffer = 500
    numBuffersToCapture = 10

    totalSamples = sizeOfOneBuffer * numBuffersToCapture

    # Create buffers ready for assigning pointers for data collection
    bufferAMax = np.zeros(shape=sizeOfOneBuffer, dtype=np.int16)
    memory_segment = 0

    # Set data buffer location for data collection from channel A
    # handle = chandle
    # source = PS5000A_CHANNEL_A = 0
    # pointer to buffer max = ctypes.byref(bufferAMax)
    # pointer to buffer min = ctypes.byref(bufferAMin)
    # buffer length = maxSamples
    # segment index = 0
    # ratio mode = PS5000A_RATIO_MODE_NONE = 0
    status["setDataBuffersA"] = ps.ps5000aSetDataBuffers(chandle,
                                                        ps.PS5000A_CHANNEL['PS5000A_CHANNEL_A'],
                                                        bufferAMax.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
                                                        None,
                                                        sizeOfOneBuffer,
                                                        memory_segment,
                                                        ps.PS5000A_RATIO_MODE['PS5000A_RATIO_MODE_NONE'])
    assert_pico_ok(status["setDataBuffersA"])