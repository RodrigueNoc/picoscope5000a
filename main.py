import time
import numpy as np
import matplotlib.pyplot as plt

import picoscope as ps

Pico = ps.Picoscope()

# Initialisation
# Start Pico
Pico.StartPico()
# Start Streaming
Pico.SetChannel('A',1,"DC","2V",0.)
Pico.SetTrigger(1,-100,"FALLING",0,0)
Pico.StartStreaming(10000,"NONE",1,0,50,'US')

# Get values
X = []
Y = []
plt.ion()
figure, ax = plt.subplots(figsize=(10, 8))
line1, = ax.plot(X, Y)
plt.title("Signal")
plt.xlabel(f"Time ({Pico.sampleIntervalTimeUnits})")
plt.ylabel("Voltage (mV)")

RUN = True
while RUN:
    Pico.GetStreamingLatestValues()
    if not Pico.wasCalledBack():
        time.sleep(0.01)
    else:
        Y = Pico.y_mV
        X = np.linspace(0, Pico.buffer_size*Pico.sampleInterval.value, Pico.buffer_size)
        line1.set_ydata(Y)
        line1.set_xdata(X)
        figure.canvas.draw()
        figure.canvas.flush_events()

# Stop Streaming
Pico.StopStreaming()
# Stop Pico
Pico.StopPico()