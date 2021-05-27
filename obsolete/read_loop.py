import numpy as np
import nidaqmx as ni
from time import sleep
from nicdaq import HallDAQ
import matplotlib.pyplot as plt
from multiprocessing import Process, Queue

startstop_q = Queue()
data_q = Queue()

daq = HallDAQ(1, 1)
daq.RATE = 50000

def readloop():
    global startstop_q, data_q, daq
    while True:
        if startstop_q.get():
            data_q.put(daq.read_hallsensor())
        else:
            break

daq.power_on()
daq.start_hallsensor_task()
startstop_q.put(True)
p1 = Process(target=readloop)
p1.start()
plt.ion()
plt.figure()
plt.plot(data_q.get())
sleep(5)
startstop_q.put(False)
p1.close()


daq.power_off()
daq.close_tasks()