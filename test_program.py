import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import zeisscmm
from nicdaq import HallDAQ
import calibration
from multiprocessing import Process, Queue
from time import sleep

def move_cmm(cmm_obj: zeisscmm.CMM, daq_obj: HallDAQ, waypoints: np.ndarray):
    for plane in waypoints:
        for point in plane:
            try:
                cmm_obj.goto_position(point)
                cmm_obj.wait(0.1)
            except KeyboardInterrupt:
                print('Shutting down')
                shutdown(cmm_obj, daq_obj)

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
    waypoints_pcs = zeisscmm.scan_volume(start_position, 50, 60, 5)
    waypoints_mcs = zeisscmm.transform_points(waypoints_pcs, T, R)
    print('waypoints_pcs')
    print(waypoints_pcs)
    print('waypoints_mcs')
    print(waypoints_mcs)
    # daq.start_hallsensor_task()
    # cmm_process = Process(target=move_cmm, args=waypoints_mcs)
    # hallsensor_process = Process(target=read_hallsensor, args=(daq,))
    # cmm_process.start()
    # hallsensor_process.start()
    move_cmm(cmm, daq, waypoints_mcs)

    # daq.stop_hallsensor_task()