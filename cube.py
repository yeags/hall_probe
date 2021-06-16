from nicdaq import HallDAQ
from calibration import get_xyz_calib_values, calib_data, orthogonalize
import zeisscmm
import numpy as np
from time import sleep

class Cube:
    def __init__(self, cube_filename: str, probe_calibration_path: str, probe_offset_filename: str):
        self.daq = HallDAQ(1, 20000, start_trigger=True, acquisition='finite')
        self.daq.power_on()
        self.cmm = zeisscmm.CMM()
        self.calib_coeffs = get_xyz_calib_values(probe_calibration_path)
        self.rotation, self.translation = self.import_cube_alignment(cube_filename)
        self.probe_offset = self.import_probe_offset(probe_offset_filename)
    
    def import_cube_alignment(self, filename: str):
        diff = np.genfromtxt(filename, delimiter=' ')
        rotation = diff[:-3].reshape((3,3))
        translation = diff[-3:]
        return (rotation, translation)
    
    def import_probe_offset(self, filename: str):
        offset = np.genfromtxt(filename, delimiter=' ')
        return offset
    
    def zero_gauss_offset():
        pass

    def measure_cube_center(self):
        pass

    def cube2mcs(self, coordinate):
        return (coordinate - self.translation)@self.rotation

    def mcs2cube(self, coordinate):
        return coordinate@np.linalg.inv(self.rotation) + self.translation
    
    def shutdown(self):
        self.cmm.close()
        self.daq.power_off()
        self.daq.close_tasks()

if __name__ == '__main__':
    test = Cube(r'D:\CMM Programs\Cube Calibration\cube_alignment.txt', r'C:\Users\dyeagly\Documents\hall_probe\hall_probe\Hall probe 444-20', r'D:\CMM Programs\FSV Calibration\hallsensor_offset_mcs.txt')
    
    test.daq.start_hallsensor_task()
    sleep(1)
    test.daq.pulse()
    data = test.daq.read_hallsensor()[7500:15000]
    cal_data = calib_data(test.calib_coeffs, data)
    cal_mean = np.mean(cal_data, axis=0)
    data_mean = np.mean(data, axis=0)
    # np.savetxt('cube_data_raw_06.txt', data, fmt='%.6f', delimiter=' ')
    with open('cube_data_senis.txt', 'a') as file:
        file.write(f'{cal_mean[0]} {cal_mean[1]} {cal_mean[2]}\n')
    # with open('zg.txt', 'a') as file:
    #     file.write(f'{data_mean[0]} {data_mean[1]} {data_mean[2]}\n')
    # print(data_mean)
    print(data_mean)
    print(cal_mean)
    # print(np.std(cal_data, axis=0, ddof=1))
    test.shutdown()