import multiprocessing as mp
from time import perf_counter
import nidaqmx as ni
from datetime import datetime

def sleep(duration, get_now=perf_counter):
    now = get_now()
    end = now + duration
    while now < end:
        now = get_now()


class Task(ni.Task):
    def __init__(self):
        super().__init__()
        self.ai_channels.add_ai_thrmcpl_chan('MagnetTemp/ai0:1', thermocouple_type=ni.constants.ThermocoupleType.K)
        self.timing.samp_timing_type = ni.constants.SampleTimingType.ON_DEMAND
        self.ai_channels.all.ai_adc_timing_mode = ni.constants.ADCTimingMode.HIGH_SPEED
        self.q_data = mp.Queue()
        self.q_status = mp.Queue()
    
    def start_task(self):
        self.start()

    def stop_task(self):
        self.stop()

    def read_temp(self):
        while True:
            if self.q_data.empty():
                self.q_data.put(self.read())
            elif self.q_status.empty() == False:
                break
            sleep(1)
    
    def create_file(self):
        self.datafile = open('mp data file ' + datetime.now().strftime('%Y-%m-%d %h-%M-%S') + '.txt', 'w')
    
    def close_file(self):
        self.datafile.close()

    def record_data(self):
        for i in range(5):
            if self.q_data.empty() == False:
                self.datafile.write(datetime.now().strftime('%Y-%m-%d-%h-%M-%S') + \
                                    '\t' + str(self.q_data.get()) + '\n')
            sleep(1.5)
        self.q_status.put(1)


if __name__ == '__main__':
    task = Task()
    task.start()
    task_q = mp.Queue()
    task_q.put(task)
    p1 = mp.Process(target=task_q.read_temp)
    p2 = mp.Process(target=task_q.record_data)
    p1.start()
    p2.start()
    p2.join()
    task.stop()
    task.close_file()
    task.close()
