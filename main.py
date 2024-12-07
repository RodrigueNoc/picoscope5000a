import ctypes
from picosdk.ps5000a import ps5000a as ps
from picosdk.functions import assert_pico_ok
from SigGen import GenSin
import time

# Setup
status = {}
chandle = ctypes.c_int16()

# Open the device
status["openUnit"] = ps.ps5000aOpenUnit(ctypes.byref(chandle), None, 1)

try:
    assert_pico_ok(status["openUnit"])
except: # PicoNotOkError:
    powerStatus = status["openUnit"]
    if powerStatus == 286:
        status["changePowerSource"] = ps.ps5000aChangePowerSource(chandle, powerStatus)
    elif powerStatus == 282:
        status["changePowerSource"] = ps.ps5000aChangePowerSource(chandle, powerStatus)
    else:
        raise
    assert_pico_ok(status["changePowerSource"])

GenSin(status,chandle)
time.sleep(5)

# Closes the unit
# Handle = chandle
status["close"] = ps.ps5000aCloseUnit(chandle)
assert_pico_ok(status["close"])

# Displays the status returns
print(status)