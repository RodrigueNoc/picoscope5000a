import ctypes
import numpy as np

from picosdk.ps5000a import ps5000a as ps
from picosdk.functions import assert_pico_ok, mV2adc

# Start pico
status = {}
chandle = ctypes.c_int16()  # chandle 'numéro de série" du pico permet d'identifier le picoscope, la fonction est en place
serial = None # ctypes.c_int8() ouvre le premier pico trouvé, si non nul ouvre le pico spécifier : 'serial number'
resolution = 1 # fonction en place => change en la valeur en la résolution du pico
status['OpenUnit'] = ps.ps5000aOpenUnit(ctypes.byref(chandle), serial, resolution)
assert_pico_ok(status['OpenUnit'])

# Setup Channel
channel = ps.PS5000A_CHANNEL['PS5000A_CHANNEL_A'] # Ouvre la voie A, valeur possible : A à D
channel_enabled = 1 # allumer 1, éteindre 0
channel_type = ps.PS5000A_COUPLING['PS5000A_DC'] # allimentation en courant continue PS5000A_DC, en courant alternatif PS5000A_AC
channel_range = ps.PS5000A_RANGE['PS5000A_2V'] # valeur possible (en valeur absolue) : PS5000A_10MV,PS5000A_20MV,PS5000A_50MV,PS5000A_100MV,PS5000A_200MV,PS5000A_500MV,PS5000A_1V,PS5000A_2V,PS5000A_5V,PS5000A_10V,PS5000A_20V,PS5000A_50V,PS5000A_MAX_RANGES
analogueOffset = 0. # Offset de 0 V pour alligner plusieurs voie par exemple
status['SetChannel'] = ps.ps5000aSetChannel(chandle,channel,channel_enabled,channel_type,channel_range,analogueOffset)
assert_pico_ok(status['SetChannel'])

# max ADC
maxADC = ctypes.c_int16()
status["maximumValue"] = ps.ps5000aMaximumValue(chandle, ctypes.byref(maxADC))
assert_pico_ok(status["maximumValue"])

# SetAutoTriggerMicroSeconds 
autoTriggerMicroseconds = ctypes.c_uint64()
status['autoTriggerMicroseconds'] = ps.ps5000aSetAutoTriggerMicroSeconds(chandle,autoTriggerMicroseconds)
assert_pico_ok(status['autoTriggerMicroseconds'])

# Set a trigger
trigger_enabled = 1 # activer 1, desactiver
trigger_threshold = mV2adc(1000, channel_range, maxADC) # the ADC count at which the trigger will fire
trigger_direction = ps.PS5000A_THRESHOLD_DIRECTION['PS5000A_RISING'] # valeur accepter : ABOVE, BELOW, RISING, FALLING et RISING_OR_FALLING
trigger_delay = 64 # time  between the trigger occurring and the first sample
trigger_autoTrigger_ms = 10 # if 0 wait indefinitely, else wait
status['SetSimpleTrigger'] = ps.ps5000aSetSimpleTrigger(chandle,trigger_enabled,channel,trigger_threshold,trigger_direction,trigger_delay,trigger_autoTrigger_ms)
assert_pico_ok(status['SetSimpleTrigger'])

# Set Tab to save Data
buffer_size = 1000
buffer_data = np.zeros(shape=buffer_size,dtype=np.int16)
buffer_mode = ps.PS5000A_RATIO_MODE['PS5000A_RATIO_MODE_NONE'] # PS5000A_RATIO_MODE_NONE,PS5000A_RATIO_MODE_AGGREGATE,PS5000A_RATIO_MODE_DECIMATE,PS5000A_RATIO_MODE_AVERAGE
status['SetDataBuffer'] = ps.ps5000aSetDataBuffer(chandle,channel,ctypes.byref(buffer_data),buffer_size,0,buffer_mode)
assert_pico_ok(status['SetDataBuffer'])

# Start Streaming
status['StartStreaming'] = ps.ps5000aRunStreaming(chandle,)
assert_pico_ok(status['StartStreaming'])

# Stop Streaming
status['StopStreaming'] = ps.ps5000aStop(chandle)
assert_pico_ok(status['StopStreaming'])

# Stop pico
status['CloseUnit'] = ps.ps5000aCloseUnit(chandle)
assert_pico_ok(status['CloseUnit'])