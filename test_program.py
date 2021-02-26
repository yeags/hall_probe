import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import zeisscmm
from nicdaq import HallDAQ
import calibration
from multiprocessing import Process, Queue
from time import sleep

def move_cmm(cmm_obj: zeisscmm.CMM, daq_obj: HallDAQ, waypoints: np.ndarray):
    daq_obj.start_hallsensor_task()
    data = []
    for plane in waypoints:
        for point in plane:
            try:
                # savefile = open('hallprobe_data.txt', 'wa')
                cmm_obj.goto_position(point)
                current_pos = cmm_obj.get_position()
                while np.linalg.norm(current_pos - point) > 0.012:
                    # sensor = read_hallsensor(cmm_obj, daq_obj)
                    # print(sensor)
                    data.append(read_hallsensor(cmm_obj, daq_obj))
                    current_pos = cmm_obj.get_position() # read current position to update while loop
                # cmm_obj.wait(0.1)
            except KeyboardInterrupt:
                print('Shutting down')
                shutdown(cmm_obj, daq_obj)
    daq_obj.stop_hallsensor_task()
    return data # Returns a list of tuples containing numpy arrays

def read_hallsensor(cmm_obj: zeisscmm.CMM, daq_obj: HallDAQ):
    position = cmm_obj.get_position()
    sample = daq_obj.read_hallsensor()
    sleep(0.1)
    return (position, sample)

def shutdown(cmm_obj: zeisscmm.CMM, daq_obj: HallDAQ):
    cmm_obj.set_speed(80)
    cmm_obj.close()
    daq_obj.power_off()
    daq_obj.close_tasks()

def parse_dataset(raw_dataset):
    cmm_xyz = []
    hall_data = []
    hall_cleaned = []
    for xyz, Bxyz in raw_dataset:
        cmm_xyz.append(xyz) # creates list of (3,) np arrays
        hall_data.append(Bxyz) # creates list of (n, 4) np arrays
    for i in hall_data:
        hall_cleaned.append(calibration.clean_raw_data(i)) # creates list of (3,) np arrays
    return np.append(cmm_xyz, hall_cleaned, axis=1) # Returns (n, 7) np array

def graph_data(cleaned_data):
    cmm_position = cleaned_data[:, :3]
    hallsensor_data = cleaned_data[:, 3:]
    hallsensor_norm = np.linalg.norm(hallsensor_data, axis=1)
    cmap = 'rainbow'


if __name__ == '__main__':
    coord_diff = np.genfromtxt('test_program/mag_test_mcs.txt', delimiter=' ')
    R = coord_diff[:9].reshape((3,3))
    T = coord_diff[9:]

    calib_coeffs = calibration.get_xyz_calib_values('Hall probe 443-20')

    cmm = zeisscmm.CMM()
    cmm.set_speed(5)
    daq = HallDAQ()

    print('Turning on hallprobe.  Range set to 2 T')
    daq.power_on()
    input('Move probe to start point')
    start_position = zeisscmm.transform_points(cmm.get_position(), T, R, inverse=True)
    waypoints_pcs = zeisscmm.scan_volume(start_position, 50, 60, 2, grid=1)
    waypoints_mcs = zeisscmm.transform_points(waypoints_pcs, T, R)
    print('waypoints_pcs')
    print(waypoints_pcs)
    print('waypoints_mcs')
    print(waypoints_mcs)
    dataset = move_cmm(cmm, daq, waypoints_mcs)
    clean_data = parse_dataset(dataset)
    np.savetxt('scan_data.txt', clean_data, header='x y z Bx By Bz TempV', encoding='utf-8')
    shutdown(cmm, daq)