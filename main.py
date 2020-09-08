from nicdaq import DAQ
from time import perf_counter
import multiprocessing as mp


def sleep(duration, get_now=perf_counter):
    end = get_now() + duration
    while end > get_now():
        pass

if __name__ == '__main__':
    daq = DAQ()
    print(daq)
    sleep(1)
    daq.close()