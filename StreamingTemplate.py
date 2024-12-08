import ctypes
import numpy as np
import time
import matplotlib.pyplot as plt

from picosdk.ps5000a import ps5000a as ps
from picosdk.functions import assert_pico_ok, mV2adc, adc2mV

# Start pico
status = {}
# chandle 'numéro de série" du pico permet d'identifier le picoscope, la fonction est en place
chandle = ctypes.c_int16()
serial = None  # ctypes.c_int8() ouvre le premier pico trouvé, si non nul ouvre le pico spécifier : 'serial number'
resolution = 1  # fonction en place => change en la valeur en la résolution du pico
status['OpenUnit'] = ps.ps5000aOpenUnit(
    ctypes.byref(chandle), serial, resolution)
assert_pico_ok(status['OpenUnit'])

# Setup Channel
# Ouvre la voie A, valeur possible : A à D
channel = ps.PS5000A_CHANNEL['PS5000A_CHANNEL_A']
channel_enabled = 1  # allumer 1, éteindre 0
# allimentation en courant continue PS5000A_DC, en courant alternatif PS5000A_AC
channel_type = ps.PS5000A_COUPLING['PS5000A_DC']
# valeur possible (en valeur absolue) : PS5000A_10MV,PS5000A_20MV,PS5000A_50MV,PS5000A_100MV,PS5000A_200MV,PS5000A_500MV,PS5000A_1V,PS5000A_2V,PS5000A_5V,PS5000A_10V,PS5000A_20V,PS5000A_50V,PS5000A_MAX_RANGES
channel_range = ps.PS5000A_RANGE['PS5000A_2V']
analogueOffset = 0.  # Offset de 0 V pour alligner plusieurs voie par exemple
status['SetChannel'] = ps.ps5000aSetChannel(
    chandle, channel, channel_enabled, channel_type, channel_range, analogueOffset)
assert_pico_ok(status['SetChannel'])

# max ADC
maxADC = ctypes.c_int16()
status["maximumValue"] = ps.ps5000aMaximumValue(chandle, ctypes.byref(maxADC))
assert_pico_ok(status["maximumValue"])

# Set a trigger
trigger_enabled = 1  # activer 1, desactiver
# the ADC count at which the trigger will fire
trigger_threshold = mV2adc(1000, channel_range, maxADC)
# valeur accepter : ABOVE, BELOW, RISING, FALLING et RISING_OR_FALLING
trigger_direction = ps.PS5000A_THRESHOLD_DIRECTION['PS5000A_FALLING']
trigger_delay = 64  # time  between the trigger occurring and the first sample
trigger_autoTrigger_ms = 10  # if 0 wait indefinitely, else wait
status['SetSimpleTrigger'] = ps.ps5000aSetSimpleTrigger(
    chandle, trigger_enabled, channel, trigger_threshold, trigger_direction, trigger_delay, trigger_autoTrigger_ms)
assert_pico_ok(status['SetSimpleTrigger'])

# Set Tab to save Data
buffer_size = 1000
buffer_data = np.zeros(shape=buffer_size, dtype=np.int16)
# PS5000A_RATIO_MODE_NONE,PS5000A_RATIO_MODE_AGGREGATE,PS5000A_RATIO_MODE_DECIMATE,PS5000A_RATIO_MODE_AVERAGE
buffer_mode = ps.PS5000A_RATIO_MODE['PS5000A_RATIO_MODE_NONE']
status['SetDataBuffer'] = ps.ps5000aSetDataBuffer(chandle, channel, buffer_data.ctypes.data_as(
    ctypes.POINTER(ctypes.c_int16)), buffer_size, 0, buffer_mode)
assert_pico_ok(status['SetDataBuffer'])

# Start Streaming
# The requested time interval between samples. On exit, the actual time interval used.
sampleInterval = ctypes.c_int32(1)
# Unit of sampleInterval, possible values : PS5000A_FS, PS5000A_PS,PS5000A_NS, PS5000A_US, PS5000A_MS, PS5000A_S
sampleIntervalTimeUnits = ps.PS5000A_TIME_UNITS['PS5000A_NS']
maxPreTriggerSamples = buffer_size*0.1
maxPostTriggerSamples = buffer_size*0.9
autoStop = 0  # Streaming will continue until stopped by ps5000aStop, else a flag that specifies if the streaming should stop when all of maxSamples = maxPreTriggerSamples + maxPostTriggerSamples have been captured and a trigger event has occurred
downSampleRatio = 1  # just value of n (look description of the next line)
# possible values : PS5000A_RATIO_MODE_NONE : Returns raw data values; PS5000A_RATIO_MODE_AGGREGATE :  Reduces every block of n values to just min and max in two buffers; PS5000A_RATIO_MODE_DECIMATE : Reduces every block of n values to just the first value in the block; PS5000A_RATIO_MODE_AVERAGE : Reduces every block of n values to arithmetic mean of all the values
downSampleRatioMode = ps.PS5000A_RATIO_MODE['PS5000A_RATIO_MODE_NONE']
overviewBufferSize = buffer_size
status['StartStreaming'] = ps.ps5000aRunStreaming(chandle, ctypes.byref(sampleInterval), sampleIntervalTimeUnits,
                                                  maxPreTriggerSamples, maxPostTriggerSamples, autoStop, downSampleRatio, downSampleRatioMode, overviewBufferSize)
assert_pico_ok(status['StartStreaming'])

# Streaming loop
actualSampleInterval = sampleInterval.value
x_time = np.linspace(0, buffer_size*actualSampleInterval, buffer_size)
y_adc = np.zeros(buffer_size)
plt.ion()
figure, ax = plt.subplots(figsize=(10, 8))
line1, = ax.plot(x_time, y_adc)
plt.title("Signal")
plt.xlabel(f"Time ({sampleIntervalTimeUnits})")
plt.ylabel("Voltage (mV)")


def streaming_callback(handle, noOfSamples, startIndex, overflow, triggerAt, triggered, autoStop, Parameter):
    """
    handle : the device identifier returned by ps5000aOpenUnit
    noOfSamples : the number of samples to collect
    startIndex : an index to the first valid sample in the buffer passed in ps5000aSetDataBuffer
    overflow : returns a set of flags that indicate whether an overvoltage has occurred on any of the channels. It is a bit pattern with bit 0 denoting Channel A.
    triggerAt : Index where are the trigger
    triggered : a flag indicating whether a trigger occurred. If non-zero, a trigger occurred at the location indicated by triggerAt.
    autoStop :  the flag that was set in the call to ps5000aRunStreaming
    Parameter : parameter pass in function at line 79

    autoStop = False => buffer is use as FIFO memory
    """
    global wasCalledBack
    wasCalledBack = True
    if triggered:
        y_adc[:] = buffer_data[:]
        y_mV = adc2mV(y_adc, channel_range, maxADC)
        line1.set_ydata(y_mV)
        figure.canvas.draw()
        figure.canvas.flush_events()


# Create a Pointer of our callback function
cPointerFunc = ps.StreamingReadyType(streaming_callback)
# Parameters will be passed in the streaming callback function in the 'Parameter' parameter
pParameter = None

RUN = True
while RUN:
    wasCalledBack = False
    status['GetStreamingLatestValues'] = ps.ps5000aGetStreamingLatestValues(
        chandle, cPointerFunc, pParameter)
    if not wasCalledBack:
        # If we weren't called back by the driver, this means no data is ready. Sleep for a short while before trying again.
        time.sleep(0.01)


# Stop Streaming
status['StopStreaming'] = ps.ps5000aStop(chandle)
assert_pico_ok(status['StopStreaming'])

# Stop pico
status['CloseUnit'] = ps.ps5000aCloseUnit(chandle)
assert_pico_ok(status['CloseUnit'])
