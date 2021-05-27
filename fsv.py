from calibration import filter_data
from nicdaq import HallDAQ
from time import sleep
import numpy as np
import zeisscmm

class FSV:
    CERAMIC_THK = 1.0
    TRACE_THK = 0.06
    GLAZE_THK = 0.01
    def __init__(self, fsv_filename: str, probe_offset_filename: str):
        self.daq = HallDAQ(1, 10000, start_trigger=True, acquisition='finite')
        self.daq.power_on()
        self.cmm = zeisscmm.CMM()
        self.rotation, self.translation = self.import_fsv_alignment(fsv_filename)
        self.probe_offset = self.import_probe_offset(probe_offset_filename)
    
    def calc_offset(self, ax: np.ndarray, B_ax: np.ndarray, filter_cutoff=500):
        '''
        ax: CMM single axis data
        B_ax: Hallsensor single axis data
        filter_cutoff: integer value used for smoothing raw sensor data,
            default set to 500
        returns: offset value for the respective CMM axis
        '''
        ax_cutoff = ax[filter_cutoff:-filter_cutoff]
        B_filtered = filter_data(B_ax, filter_cutoff)[filter_cutoff:-filter_cutoff]
        combined_array = np.array([ax_cutoff, B_filtered]).T
        array_min = combined_array[combined_array[:, 1] == combined_array[:, 1].min()][0,0]
        array_max = combined_array[combined_array[:, 1] == combined_array[:, 1].max()][0,0]
        offset = (array_max + array_min) / 2
        return offset

    def import_fsv_alignment(self, filename: str):
        diff = np.genfromtxt(filename, delimiter=' ')
        rotation = diff[:-3].reshape((3,3))
        translation = diff[-3:]
        return (rotation, translation)
    
    def import_probe_offset(self, filename: str):
        offset = np.genfromtxt(filename, delimiter=' ')
        return offset

    def fsv2mcs(self, coordinate: np.ndarray):
        return (coordinate - self.translation)@self.rotation

    def mcs2fsv(self, coordinate: np.ndarray):
        return coordinate@np.linalg.inv(self.rotation) + self.translation

    def perform_scan(self, start_pt, end_pt, speed=5, direction='positive'):
        '''
        direction can either be 'positive' or 'negative'
        '''
        self.cmm.cnc_on()
        self.cmm.set_speed(speed)
        self.cmm.goto_position(start_pt)
        while np.linalg.norm(start_pt - self.cmm.get_position()) > 0.025:
            pass
        self.daq.fsv_on(v=direction)
        self.daq.start_hallsensor_task()
        sleep(1) # Allow time for task to start.
        self.cmm.goto_position(end_pt)
        sleep(1) # Allow time for CMM to finish accelerating
        self.daq.pulse()
        start_position = self.mcs2fsv(self.cmm.get_position())
        data = self.daq.read_hallsensor()
        end_position = self.mcs2fsv(self.cmm.get_position())
        self.daq.fsv_off()
        self.daq.stop_hallsensor_task()
        self.cmm.set_speed(70)
        self.cmm.cnc_off()
        return (start_position, end_position, data)

    def run_x_routine(self):
        half_length = np.array([20, 0, 0])
        current_pos_fsv = self.mcs2fsv(self.cmm.get_position())
        start_pos_mcs = self.fsv2mcs(current_pos_fsv - half_length)
        end_pos_mcs = self.fsv2mcs(current_pos_fsv + half_length)
        start_p, end_p, data_p = self.perform_scan(start_pos_mcs, end_pos_mcs, speed=5)
        x_p = np.linspace(start_p[0], end_p[0], data_p.shape[0])
        sleep(1)
        start_n, end_n, data_n = self.perform_scan(end_pos_mcs, start_pos_mcs, direction='negative')
        x_n = np.linspace(start_n[0], end_n[0], data_n.shape[0])
        combined_p = np.insert(data_p, 0, x_p, axis=1) # (x, Bx, By, Bz, Btemp)
        combined_n = np.insert(data_n, 0, x_n, axis=1) # (x, Bx, By, Bz, Btemp)
        np.savetxt('x_pos_i.txt', combined_p, fmt='%.6f', delimiter=' ')
        np.savetxt('x_neg_i.txt', combined_n, fmt='%.6f', delimiter=' ')
        # return (combined_p, combined_n)
        data_pn = data_p - data_n
        x_pn = (x_p + x_n) / 2
        # x_p_offset = self.calc_offset(x_p, data_p[:, 2])
        # x_n_offset = self.calc_offset(x_n, data_n[:, 2])
        # return (x_p_offset, x_n_offset)
        data_pn_offset = self.calc_offset(x_pn, data_pn[:, 2])
        return data_pn_offset

    def run_y_routine(self):
        half_length = np.array([0, 20, 0])
        current_pos_fsv = self.mcs2fsv(self.cmm.get_position())
        start_pos_mcs = self.fsv2mcs(current_pos_fsv - half_length)
        end_pos_mcs = self.fsv2mcs(current_pos_fsv + half_length)
        start_p, end_p, data_p = self.perform_scan(start_pos_mcs, end_pos_mcs)
        y_p = np.linspace(start_p[1], end_p[1], data_p.shape[0])
        sleep(1)
        start_n, end_n, data_n = self.perform_scan(end_pos_mcs, start_pos_mcs, direction='negative')
        y_n = np.linspace(start_n[1], end_n[1], data_n.shape[0])
        # combined_p = np.insert(data_p, 0, y_p, axis=1) # (y, Bx, By, Bz, Btemp)
        # combined_n = np.insert(data_n, 0, y_n, axis=1) # (y, Bx, By, Bz, Btemp)
        # return (combined_p, combined_n)
        y_p_offset = self.calc_offset(y_p, data_p[:, 2])
        y_n_offset = self.calc_offset(y_n, data_n[:, 2])
        return (y_p_offset, y_n_offset)

    def run_z_routine(self):
        half_length = np.array([0, 0, 20])
        current_pos_fsv = self.mcs2fsv(self.cmm.get_position())
        start_pos_mcs = self.fsv2mcs(current_pos_fsv - half_length)
        end_pos_mcs = self.fsv2mcs(current_pos_fsv + half_length)
        start_p, end_p, data_p = self.perform_scan(start_pos_mcs, end_pos_mcs)
        z_p = np.linspace(start_p[2], end_p[2], data_p.shape[0])
        sleep(1)
        start_n, end_n, data_n = self.perform_scan(end_pos_mcs, start_pos_mcs, direction='negative')
        z_n = np.linspace(start_n[2], end_n[2], data_n.shape[0])
        # combined_p = np.insert(data_p, 0, z_p, axis=1) # (z, Bx, By, Bz, Btemp)
        # combined_n = np.insert(data_n, 0, z_n, axis=1) # (z, Bx, By, Bz, Btemp)
        # return (combined_p, combined_n)
        z_p_offset = self.calc_offset(z_p, data_p[:, 0])
        z_n_offset = self.calc_offset(z_n, data_n[:, 0])
        return (z_p_offset, z_n_offset)

    def save_probe_offset(self):
        pass

    def shutdown(self):
        self.cmm.close()
        self.daq.power_off()
        self.daq.close_tasks()

if __name__ == '__main__':
    test = FSV(r'D:\CMM Programs\FSV Calibration\fsv_alignment.txt', r'D:\CMM Programs\FSV Calibration\probe_offset.txt')
    # pos_offset, neg_offset = test.run_x_routine()
    # print(f'positive offset: {round(pos_offset, 3)}\nnegative offset: {round(neg_offset, 3)}')
    # print(f'offset difference: {round(pos_offset - neg_offset, 3)}')
    offset = test.run_x_routine()
    print(f'offset: {round(offset, 3)}')
    test.shutdown()
    # np.savetxt('bz_positive.txt', data_p, fmt='%.6f', delimiter=' ')
    # np.savetxt('bz_negative.txt', data_n, fmt='%.6f', delimiter=' ')