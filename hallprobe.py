from nicdaq import HallDAQ
import zeisscmm
import numpy as np
from time import time
import threading
from calibration import remove_outliers, average_sample

class HallProbe:
    def __init__(self):
        self.halldaq = HallDAQ()
        self.cmm = zeisscmm.CMM()
    
    def __repr__(self):
        return 'Integrated Hall Probe Object'

    def scan_point(self, point):
        if point == None:
            point = self.cmm.get_position()
        else:
            self.cmm.cnc_on()
            self.cmm.goto_position(point)
            self.cmm.wait(1)
            self.cmm.cnc_off()
        self.halldaq.power_on()
        self.halldaq.start_hallsensor_task()
        self.halldaq.start_magnet_temp_task()
        dt = time()
        current_pos = self.cmm.get_position()
        hs_raw = self.halldaq.read_hallsensor()
        mt_raw = self.halldaq.read_magnet_temp()
        self.halldaq.stop_hallsensor_task()
        self.halldaq.stop_magnet_temp_task()
        self.halldaq.power_off()
        return (dt, current_pos, hs_raw, mt_raw)

    def scan_line(self, start_point, end_point):
        dt_list = []
        xyz_list = []
        hs_list = []
        mt_list = []
        self.halldaq.power_on()
        self.cmm.cnc_on()
        self.cmm.goto_position(start_point)
        self.cmm.wait(0.1)
        self.halldaq.start_hallsensor_task()
        self.halldaq.start_magnet_temp_task()
        current_pos = self.cmm.get_position()
        self.cmm.set_speed(5)
        try:
            self.cmm.goto_position(end_point)
            while np.linalg.norm(current_pos - end_point) > 0.012:
                dt_list.append(time())
                xyz_list.append(self.cmm.get_position())
                hs_list.append(self.halldaq.read_hallsensor())
                mt_list.append(self.halldaq.read_magnet_temp())
                current_pos = self.cmm.get_position()
        except KeyboardInterrupt:
            print('Shutting down')
            self.cmm.cnc_off()
            self.cmm.set_speed(80)
            self.shutdown_hallprobe()
            return False
        self.halldaq.stop_hallsensor_task()
        self.halldaq.stop_magnet_temp_task()
        # self.halldaq.power_off()
        self.cmm.cnc_off()
        self.cmm.set_speed(80)
        print('dt_list:', type(dt_list[0]), dt_list[0])
        print('xyz_list:', type(xyz_list[0]), xyz_list[0])
        print('hs_list:', type(hs_list[0]), hs_list[0])
        print('mt_list:', type(mt_list[0]), mt_list[0])
        for i, sample in enumerate(hs_list):
            if i==50:
                print('hs_sample[50]:', sample.shape)
            no_outliers = remove_outliers(sample)
            avg_sample = average_sample(no_outliers)
            hs_list[i] = avg_sample
        for i, sample in enumerate(mt_list):
            no_outliers = remove_outliers(sample)
            avg_sample = average_sample(sample)
            mt_list[i] = avg_sample
        dt_list = np.array(dt_list)
        print('dt_list:', dt_list.shape, dt_list[0])
        print('xyz_list:', xyz_list[0])
        print('hs_list:', hs_list[0])
        print('mt_list:', mt_list[0])
        return (dt_list, xyz_list, hs_list, mt_list)

    def scan_area(self, start_point, x_length, y_length, grid=0.5):
        waypoints = zeisscmm.generate_scan_area(start_point, x_length, y_length, grid=grid)
        dt_list = []
        xyz_list = []
        hs_list = []
        mt_list = []
        self.cmm.cnc_on()
        self.cmm.set_speed(5)
        for point in waypoints:
            try:
                self.cmm.goto_position(point)
                current_pos = self.cmm.get_position()
                while np.linalg.norm(current_pos - point) > 0.012:
                    dt_list.append(time())
                    xyz_list.append(self.cmm.get_position())
                    hs_list.append(self.halldaq.read_hallsensor())
                    mt_list.append(self.halldaq.read_magnet_temp())
            except KeyboardInterrupt:
                print('Shutting down')
                self.cmm.cnc_off()
                self.cmm.set_speed(80)
                self.shutdown_hallprobe()
                return False
        self.cmm.cnc_off()
        self.cmm.set_speed(80)
        return (dt_list, xyz_list, hs_list, mt_list)

    def scan_volume(self):
        pass

    def shutdown_hallprobe(self):
        if self.halldaq.power_status:
            self.halldaq.power_off()
        
        self.halldaq.close_tasks()
        self.cmm.close()
        

if __name__ == '__main__':
    '''
    Function test
    '''
    coord_diff = np.genfromtxt('test_program/mag_test_mcs.txt', delimiter=' ')
    R = coord_diff[:9].reshape((3,3))
    T = coord_diff[9:]

    hp = HallProbe()
    # Test scan_point
    point = [1045,-2615,-988]
    waypoints_pcs = np.array([[-15.,40., 120.],
                              [40., 40., 120.]])
    waypoints_mcs = zeisscmm.transform_points(waypoints_pcs, T, R)
    # hp.scan_point(point)
    scan_data = hp.scan_line(waypoints_mcs[0], waypoints_mcs[1])
    # np.savetxt('scan_line_data.txt', scan_data, fmt='%.6f')
    hp.shutdown_hallprobe()
