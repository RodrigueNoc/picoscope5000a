import time
import numpy as np

import picoscope as ps

Pico = ps.Picoscope()

# Initialisation
Pico.StartPico()
Pico.SetChannel('A',1,"DC","2V",0.)
Pico.SetTrigger(1,-100,"FALLING",0,0)
Pico.StartStreaming(10000,"NONE",1,0,50,'US')

# 
RUN = True
while RUN:
    Pico.GetStreamingLatestValues()
    if not Pico.wasCalledBack():
        time.sleep(0.01)
    else:
        Y = Pico.y_mV
        X = np.linspace(0, Pico.buffer_size*Pico.sampleInterval.value, Pico.buffer_size)

# Stop
Pico.StopStreaming()
Pico.StopPico()