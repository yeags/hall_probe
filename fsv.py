from calibration import filter_data, get_xyz_calib_values, calib_data
from nicdaq import HallDAQ
from time import sleep
import numpy as np
import zeisscmm
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
from datetime import datetime

class FSV:
    CERAMIC_THK = 1.0
    TRACE_THK = 0.06
    GLAZE_THK = 0.01
    TRACE_Z_OFFSET = 0.242

    def __init__(self, fsv_filename: str, probe_calibration_array: np.ndarray):
        self.daq = HallDAQ(1, 10000, start_trigger=True, acquisition='finite')
        self.daq.power_on()
        self.cmm = zeisscmm.CMM()
        self.rotation, self.translation = self.import_fsv_alignment(fsv_filename)
        self.calibration_coeffs = probe_calibration_array
    
    def calc_offset(self, data_pos: np.ndarray, data_neg: np.ndarray, filter_cutoff=500, fit_lc=125):
        '''
        data_pos: (n, 2) array of sample data (ex. [x, bz])
        data_neg: (n, 2) array of sample data (current reversed)
        filter_cutoff: integer value used for smoothing raw sensor data,
            default set to 500
        fit_lc: extra samples to cut off for better linear fit default set to 175
        returns: offset value for the respective CMM axis
        '''
        # Filter hallsensor data
        dpf = filter_data(data_pos[:, 1], filter_cutoff)
        dnf = filter_data(data_neg[:, 1], filter_cutoff)
        # Filter noisy data and cutoff beginning/end
        dpf_cutoff = dpf[filter_cutoff:-filter_cutoff]
        dnf_cutoff = dnf[filter_cutoff:-filter_cutoff]
        # Find min/max indices of filtered data and incorporate additional sample cutoff (fit_lc)
        dpf_min_index = np.where(dpf_cutoff == dpf_cutoff.min())[0][0] + filter_cutoff + fit_lc
        dpf_max_index = np.where(dpf_cutoff == dpf_cutoff.max())[0][0] + filter_cutoff - fit_lc
        dnf_min_index = np.where(dnf_cutoff == dnf_cutoff.min())[0][0] + filter_cutoff + fit_lc
        dnf_max_index = np.where(dnf_cutoff == dnf_cutoff.max())[0][0] + filter_cutoff - fit_lc
        try:
            dpf_polyfit = np.polyfit(data_pos[:, 0][dpf_min_index:dpf_max_index], dpf[dpf_min_index:dpf_max_index], 3)
            dnf_polyfit = np.polyfit(data_neg[:, 0][dnf_min_index:dnf_max_index], dnf[dnf_min_index:dnf_max_index], 3)
        except TypeError:
            dpf_polyfit = np.polyfit(data_pos[:, 0][dpf_max_index:dpf_min_index], dpf[dpf_max_index:dpf_min_index], 3)
            dnf_polyfit = np.polyfit(data_neg[:, 0][dnf_max_index:dnf_min_index], dnf[dnf_max_index:dnf_min_index], 3)
        
        diff = dpf_polyfit - dnf_polyfit
        # print(f'diff: {diff}')
        # print(f'diff[1]: {diff[1]}')
        roots = np.roots(diff)
        print(f'roots: {roots}')
        if diff[1] == complex:
            offset = roots[(roots > np.min(roots)) & (roots < np.max(roots))].real
        else:
            offset = roots[(roots > np.min(roots)) & (roots < np.max(roots))]
        print(f'offset: {offset}')
        return offset

    def import_fsv_alignment(self, filename: str):
        diff = np.genfromtxt(filename, delimiter=' ')
        rotation = diff[:9].reshape((3,3))
        translation = diff[9:]
        return (rotation, translation)

    def fsv2mcs(self, coordinate: np.ndarray):
        return (coordinate - self.translation)@self.rotation

    def mcs2fsv(self, coordinate: np.ndarray):
        return coordinate@np.linalg.inv(self.rotation) + self.translation

    def perform_scan(self, start_pt, end_pt, speed=(5,5,5), sensitivity=100, direction='positive'):
        '''
        direction can either be 'positive' or 'negative'
        sensitivity should either be 5 V/T or 100 V/T
        '''
        self.cmm.cnc_on()
        self.cmm.set_speed(speed)
        self.cmm.goto_position(start_pt)
        while np.linalg.norm(start_pt - self.cmm.get_position()) > 0.025:
            print(f'waiting for CMM to reach start position: {np.linalg.norm(start_pt - self.cmm.get_position())}')
            sleep(0.2)
        print(f'CMM speed limits: X {round(speed[0], 1)}\tY {round(speed[1], 1)}\TZ {round(speed[2], 1)}')
        self.cmm.set_speed(speed)
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
        self.cmm.set_speed((70,70,70))
        self.cmm.cnc_off()
        cal_data = calib_data(self.calibration_coeffs, data, sensitivity=sensitivity)
        return (start_position, end_position, cal_data)

    def run_x_routine(self):
        half_length = np.array([20, 0, 0])
        current_pos_fsv = self.mcs2fsv(self.cmm.get_position())
        start_pos_mcs = self.fsv2mcs(current_pos_fsv - half_length)
        end_pos_mcs = self.fsv2mcs(current_pos_fsv + half_length)
        self.daq.change_sensitivity(sensitivity='100MT')
        # Scan +
        speed_direction_vector = 5 * np.abs((end_pos_mcs - start_pos_mcs) / np.linalg.norm(end_pos_mcs - start_pos_mcs))
        start_p, end_p, data_p = self.perform_scan(start_pos_mcs, end_pos_mcs, speed=speed_direction_vector)
        x_p = np.linspace(start_p[0], end_p[0], data_p.shape[0])
        sleep(1)
        # Scan -
        start_n, end_n, data_n = self.perform_scan(self.cmm.get_position(), start_pos_mcs, speed=speed_direction_vector, direction='negative')
        x_n = np.linspace(start_n[0], end_n[0], data_n.shape[0])
        # Combine CMM and hallsensor data into one array
        combined_p = np.insert(data_p, 0, x_p, axis=1) # (x, Bx, By, Bz)
        combined_n = np.insert(data_n, 0, x_n, axis=1) # (x, Bx, By, Bz)
        # save data to file
        np.savetxt('fsv_x_pos.txt', combined_p, delimiter=' ', fmt='%.3f')
        np.savetxt('fsv_x_neg.txt', combined_n, delimiter=' ', fmt='%.3f')
        data_pn_offset = self.calc_offset(combined_p[:, [0, 3]], combined_n[:, [0, 3]])
        self.x_offset_fsv = data_pn_offset - (self.TRACE_THK/2 + self.GLAZE_THK)
        print(f'x offset: {self.x_offset_fsv}')

    def run_y_routine(self):
        half_length = np.array([0, 20, 0])
        current_pos_fsv = self.mcs2fsv(self.cmm.get_position())
        start_pos_mcs = self.fsv2mcs(current_pos_fsv - half_length)
        end_pos_mcs = self.fsv2mcs(current_pos_fsv + half_length)
        self.daq.change_sensitivity(sensitivity='100MT')
        # Scan +
        speed_direction_vector = 5 * np.abs((end_pos_mcs - start_pos_mcs) / np.linalg.norm(end_pos_mcs - start_pos_mcs))
        start_p, end_p, data_p = self.perform_scan(start_pos_mcs, end_pos_mcs, speed=speed_direction_vector)
        y_p = np.linspace(start_p[1], end_p[1], data_p.shape[0])
        sleep(1)
        # Scan -
        start_n, end_n, data_n = self.perform_scan(self.cmm.get_position(), start_pos_mcs, speed=speed_direction_vector, direction='negative')
        y_n = np.linspace(start_n[1], end_n[1], data_n.shape[0])
        combined_p = np.insert(data_p, 0, y_p, axis=1) # (y, Bx, By, Bz)
        combined_n = np.insert(data_n, 0, y_n, axis=1) # (y, Bx, By, Bz)
        # Save data to file
        np.savetxt('fsv_y_pos.txt', combined_p, delimiter=' ', fmt='%.3f')
        np.savetxt('fsv_y_neg.txt', combined_n, delimiter=' ', fmt='%.3f')
        data_pn_offset = self.calc_offset(combined_p[:, [0, 3]], combined_n[:, [0, 3]])
        self.y_offset_fsv = data_pn_offset - (self.TRACE_THK/2 + self.GLAZE_THK)
        print(f'y offset: {self.y_offset_fsv}')

    def run_z_routine(self):
        half_length = np.array([0, 0, 20])
        current_pos_fsv = self.mcs2fsv(self.cmm.get_position())
        start_pos_mcs = self.fsv2mcs(current_pos_fsv - half_length)
        end_pos_mcs = self.fsv2mcs(current_pos_fsv + half_length)
        # Set hall probe to high sensitivity
        self.daq.change_sensitivity(sensitivity='100MT')
        # Scan +
        speed_direction_vector = 5 * np.abs((end_pos_mcs - start_pos_mcs) / np.linalg.norm(end_pos_mcs - start_pos_mcs))
        start_p, end_p, data_p = self.perform_scan(start_pos_mcs, end_pos_mcs, speed=speed_direction_vector, sensitivity=100, direction='negative')
        z_p = np.linspace(start_p[2], end_p[2], data_p.shape[0])
        sleep(1)
        # Scan -
        start_n, end_n, data_n = self.perform_scan(self.cmm.get_position(), start_pos_mcs, speed=speed_direction_vector, sensitivity=100)
        z_n = np.linspace(start_n[2], end_n[2], data_n.shape[0])
        combined_p = np.insert(data_p, 0, z_p, axis=1) # (z, Bx, By, Bz)
        combined_n = np.insert(data_n, 0, z_n, axis=1) # (z, Bx, By, Bz)
        # Save data to file
        np.savetxt('fsv_z_pos.txt', combined_p, delimiter=' ', fmt='%.3f')
        np.savetxt('fsv_z_neg.txt', combined_n, delimiter=' ', fmt='%.3f')
        data_pn_offset = self.calc_offset(combined_p[:, [0, 1]], combined_n[:, [0, 1]])
        self.z_offset_fsv = data_pn_offset + self.TRACE_Z_OFFSET
        print(f'z offset: {self.z_offset_fsv}')

    def save_probe_offset(self):
        offset_mcs = np.array([self.x_offset_fsv, self.y_offset_fsv, self.z_offset_fsv]).reshape((3,))@self.rotation
        now = datetime.now()
        now_str = now.strftime('%Y-%m-%d %H-%M-%S')
        with open('fsv_offset.txt', 'w') as file:
            file.write(f'{offset_mcs[0]} {offset_mcs[1]} {offset_mcs[2]}\n')
        with open(f'fsv_offset backup {now_str}.txt', 'w') as file:
            file.write(f'{offset_mcs[0]} {offset_mcs[1]} {offset_mcs[2]}\n')

    def shutdown(self):
        self.cmm.close()
        self.daq.power_off()
        self.daq.close_tasks()

class fsvWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent, takefocus=True)
        self.fsv = None
        self.fsv_filename = None
        self.calib_coeffs = None
        self.title('FSV Qualification')
        self.frm_fsv_window = tk.Frame(self)
        self.frm_fsv_window.pack()
        self.img_fsv_x = ImageTk.PhotoImage(Image.open('images/fsv_x.jpg'))
        self.img_fsv_y = ImageTk.PhotoImage(Image.open('images/fsv_y.jpg'))
        self.img_fsv_z = ImageTk.PhotoImage(Image.open('images/fsv_z.jpg'))
        self.create_widgets()
    
    def __shutdown_tasks__(self):
        if self.fsv:
            self.fsv.shutdown()
        self.destroy()
    
    def create_widgets(self):
        self.btn_load_alignment = ttk.Button(self.frm_fsv_window, text='Load FSV Alignment', command=self.load_alignment)
        self.btn_load_calibration = ttk.Button(self.frm_fsv_window, text='Load Sensor Calibration', command=self.load_calibration)
        self.btn_run_x = ttk.Button(self.frm_fsv_window, text='Run X Offset', command=lambda: self.run_fsv(offset='x'), state='disabled')
        self.btn_run_y = ttk.Button(self.frm_fsv_window, text='Run Y Offset', command=lambda: self.run_fsv(offset='y'), state='disabled')
        self.btn_run_z = ttk.Button(self.frm_fsv_window, text='Run Z Offset', command=lambda: self.run_fsv(offset='z'), state='disabled')
        self.btn_close = ttk.Button(self.frm_fsv_window, text='Close', command=self.__shutdown_tasks__)
        self.btn_load_alignment.grid(column=0, row=0, padx=5, pady=5)
        self.btn_load_calibration.grid(column=0, row=1, padx=5, pady=5)
        self.btn_run_x.grid(column=0, row=2, padx=5, pady=5)
        self.btn_run_y.grid(column=0, row=3, padx=5, pady=5)
        self.btn_run_z.grid(column=0, row=4, padx=5, pady=5)
        self.btn_close.grid(column=0, row=5, padx=5, pady=5)
        self.btn_run_x.bind('<Button-1>', lambda event: self.lbl_desc.configure(text='Please wait.  X offset routine running...'))
        self.btn_run_y.bind('<Button-1>', lambda event: self.lbl_desc.configure(text='Please wait.  Y offset routine running...'))
        self.btn_run_z.bind('<Button-1>', lambda event: self.lbl_desc.configure(text='Please wait.  Z offset routine running...'))

    def load_alignment(self):
        self.fsv_filename = filedialog.askopenfilename(filetypes=[('Text Files', '*.txt'), ('All Files', '*.*')])
        if (self.fsv_filename and self.calib_coeffs) is not None:
            self.btn_run_x.configure(state='enabled')
            self.load_image(self.img_fsv_x, offset_axis='x')
        self.focus()
    
    def load_calibration(self):
        calib_folder = filedialog.askdirectory()
        self.calib_coeffs = get_xyz_calib_values(calib_folder)
        zg_offset = np.genfromtxt('zg_offset.txt')
        self.calib_coeffs[:, 2, 0] = -zg_offset
        np.save('zg_calib_coeffs.npy', self.calib_coeffs, allow_pickle=False)
        if (self.fsv_filename and self.calib_coeffs) is not None:
            self.btn_run_x.configure(state='enabled')
            self.load_image(self.img_fsv_x, offset_axis='x')
            self.focus()
    
    def load_image(self, image, offset_axis='x'):
        try:
            self.lbl_desc.configure(text=f'Move probe over fsv tool as shown and run {offset_axis} offset')
            self.lbl_img.configure(image=image)
        except:
            self.lbl_desc = tk.Label(self.frm_fsv_window, text=f'Move probe over fsv tool as shown and run {offset_axis} offset.')
            self.lbl_img = tk.Label(self.frm_fsv_window, image=image)
            self.lbl_desc.grid(column=1, row=0, padx=5, pady=5, sticky='w')
            self.lbl_img.grid(column=1, row=1, padx=5, pady=5, rowspan=5)
    
    def run_fsv(self, offset='x'):
        if (self.fsv_filename and self.calib_coeffs) is None:
            messagebox.showerror(title='Error', message='Load alignment and calibration files first.')
        else:
            if self.fsv is None:
                self.fsv = FSV(self.fsv_filename, self.calib_coeffs)
            if offset == 'x':
                self.fsv.run_x_routine()
                self.btn_run_x.configure(state='disabled')
                self.btn_run_y.configure(state='enabled')
                self.load_image(self.img_fsv_y, offset_axis='y')
            elif offset == 'y':
                self.fsv.run_y_routine()
                self.btn_run_y.configure(state='disabled')
                self.btn_run_z.configure(state='enabled')
                self.load_image(self.img_fsv_z, offset_axis='z')
            elif offset == 'z':
                self.fsv.run_z_routine()
                self.btn_run_z.configure(state='disabled')
                self.fsv.save_probe_offset()
                # self.fsv.shutdown()
                self.lbl_desc.configure(text='xyz offset routines complete.  You may now close the window.')


if __name__ == '__main__':
    pass
    