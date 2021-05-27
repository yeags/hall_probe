from multiprocessing import Process, Queue
import matplotlib.pyplot as plt
from nicdaq import HallDAQ
import numpy as np
from time import sleep

def read(queue_obj: Queue):
    daq_obj = HallDAQ(1,1)
    daq_obj.power_on()
    daq_obj.start_hallsensor_task()
    try:
        while True:
            queue_obj.put(daq_obj.read_hallsensor())
            sleep(.5)
    except KeyboardInterrupt:
        daq_obj.stop_hallsensor_task()
        daq_obj.power_off()

def plot(queue_obj: Queue):
    plt.ion()
    fig, ax = plt.subplots()
    ax.set_xlim(0, 100)
    ax.set_ylim(-2, 2)
    ax.grid()
    i = 0
    try:
        while queue_obj.empty():
            pass
        while True:
            Bx, By, Bz, Tv = np.mean(queue_obj.get(), axis=0)
            ax.scatter(i, Bx, marker=',', color='C0')
            ax.scatter(i, By, marker=',', color='C1')
            ax.scatter(i, Bz, marker=',', color='C2')
            plt.pause(0.005)
            i += 1
    except KeyboardInterrupt:
        plt.ioff()
        plt.close()

if __name__ == '__main__':
    q = Queue()
    p1 = Process(target=read, args=(q,))
    p2 = Process(target=plot, args=(q,))
    print('Starting read loop')
    p1.start()
    print('Starting plot loop')
    p2.start()