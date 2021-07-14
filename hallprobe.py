from os import remove
from nicdaq import HallDAQ
import zeisscmm
import numpy as np
from time import time, sleep, perf_counter
from calibration import calib_data, remove_outliers, average_sample

class HallProbe(HallDAQ):
    def __init__(self, rate, samps_per_chan, start_trigger=True, acquisition='finite'):
        super().__init__(rate, samps_per_chan, start_trigger, acquisition)
        self.calib_coeffs = np.load('zg_calib_coeffs.npy')
        self.s_matrix = np.load('sensitivity.npy')
        self.probe_offset = np.genfromtxt('fsv_offset.txt')
        self.cmm = zeisscmm.CMM()
        self.sample_rate = self.__determine_sample_rate__()
        self.scan_speed = 5
    
    def __repr__(self):
        return 'Integrated Hall Probe Object'
    
    def __determine_sample_rate__(self):
        self.power_on()
        self.start_hallsensor_task()
        sleep(1)
        start = perf_counter()
        self.pulse()
        self.read_hallsensor()
        end = perf_counter()
        self.stop_hallsensor_task()
        self.power_off()
        sample_rate = self.SAMPLES_CHAN / (end - start)
        return sample_rate

    def scan_point(self, *point):
        if not point:
            point = self.cmm.get_position()
            self.power_on()
            self.start_hallsensor_task()
            sleep(1)
            self.pulse()
            data = self.read_hallsensor()
            cal_data = calib_data(self.calib_coeffs, data)
            self.power_off()
            self.stop_hallsensor_task()
            return (point, average_sample(remove_outliers(cal_data)))
        else:
            point = point[0]
            self.cmm.cnc_on()
            self.cmm.set_speed(40)
            self.cmm.goto_position(point)
            while np.linalg.norm(point - self.cmm.get_position()) > 0.025:
                pass
            self.power_on()
            self.start_hallsensor_task()
            sleep(1)
            self.pulse()
            data = self.read_hallsensor()
            cal_data = calib_data(self.calib_coeffs, data)
            self.cmm.set_speed(70)
            self.cmm.cnc_off()
            self.power_off()
            self.stop_hallsensor_task()
            return (point, self.s_matrix@average_sample(remove_outliers(cal_data)))

    def scan_line(self, start_point, end_point):
        distance = np.linalg.norm(end_point - start_point)
        travel_time = distance / self.scan_speed
        samples = int((travel_time * self.sample_rate) - 2 * self.sample_rate)
        self.change_sampling(1, samples)
        self.cmm.goto_position(start_point)
        while np.linalg.norm(start_point - self.cmm.get_position()) > 0.025:
            pass
        self.start_hallsensor_task()
        sleep(1)
        self.cmm.goto_position(end_point)
        sleep(1)
        self.pulse()
        start_pt = self.cmm.get_position()
        data = self.read_hallsensor()
        end_pt = self.cmm.get_position()
        while np.linalg.norm(end_point - self.cmm.get_position()) > 0.025:
            pass
        self.stop_hallsensor_task()
        self.power_off()
        cal_data = calib_data(self.calib_coeffs, data)
        for i, sample in cal_data:
            cal_data[i] = self.s_matrix@sample
        linear = np.linspace(start_pt, end_pt, num=samples)
        return (linear, cal_data)
        

    def scan_area(self, start_point, x_length, y_length, grid=0.5):
        pass

    def scan_volume(self):
        pass
        

if __name__ == '__main__':
    pass
