from nicdaq import HallDAQ
from calibration import get_xyz_calib_values, calib_data, orthogonalize
from zeisscmm import CMM
import numpy as np
from time import sleep
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk

class Cube:
    def __init__(self, cube_alignment_filename: str,\
                 calibration_array: np.ndarray,\
                 probe_offset_filename: str):
        self.cube_dict = {}
        self.daq = HallDAQ(1, 20000, start_trigger=True, acquisition='finite')
        self.daq.power_on()
        self.cmm = CMM()
        self.calib_coeffs = calibration_array
        self.rotation, self.translation = self.load_cube_alignment(cube_alignment_filename)
        self.probe_offset = np.genfromtxt(probe_offset_filename)
        self.cube_origin_mcs = (np.zeros((3,)) - self.translation)@self.rotation + self.probe_offset
    
    def cube2mcs(self, coordinate):
        return (coordinate - self.translation)@self.rotation

    def mcs2cube(self, coordinate):
        return coordinate@np.linalg.inv(self.rotation) + self.translation

    def load_cube_alignment(self, filename: str):
        diff = np.genfromtxt(filename, delimiter=' ')
        rotation = diff[:-3].reshape((3,3))
        translation = diff[-3:]
        return (rotation, translation)

    def measure(self, cube_dict_key: str):
        self.daq.start_hallsensor_task()
        sleep(1)
        self.daq.pulse()
        data = self.daq.read_hallsensor()[7500:15000]
        self.daq.stop_hallsensor_task()
        cal_data = calib_data(self.calib_coeffs, data)
        self.cube_dict[cube_dict_key] = np.mean(cal_data, axis=0)

    def shutdown(self):
        self.cmm.close()
        self.daq.power_off()
        self.daq.close_tasks()
    
class CubeWindow(tk.Toplevel):
    def __init__(self, parent):
        self.cube_sequence = [2, 3, 4, 1,
                              16, 8, 9, 19,
                              20, 23, 12, 7]
        self.cube = None
        self.click_index = None
        self.calib_array = np.load('zg_calib_coeffs.npy')
        self.images = self.__create_image_dict__()
        super().__init__(parent)
        self.title('Sensor Orthogonalization')
        self.frm_cube_window = tk.Frame(self)
        self.frm_cube_window.pack()
        self.create_widgets()
    
    def __create_image_dict__(self):
        image_dict = {}
        self.keys = ['x1', 'x2', 'x3', 'x4', 'y1', 'y2', 'y3', 'y4', 'z1', 'z2', 'z3', 'z4']
        images = ['images/cube_x1.jpg', 'images/cube_x2.jpg', 'images/cube_x3.jpg', 'images/cube_x4.jpg',
                  'images/cube_y1.jpg', 'images/cube_y2.jpg', 'images/cube_y3.jpg', 'images/cube_y4.jpg',
                  'images/cube_z1.jpg', 'images/cube_z2.jpg', 'images/cube_z3.jpg', 'images/cube_z4.jpg']
        for i in range(12):
            image_dict[self.keys[i]] = ImageTk.PhotoImage(Image.open(images[i]))
        return image_dict
    
    def create_widgets(self):
        self.btn_load_alignment = ttk.Button(self.frm_cube_window,
                                             text='Load Cube Alignment',
                                             command=self.load_alignment)
        self.btn_measure_cube_center = ttk.Button(self.frm_cube_window,
                                                  text='Measure Cube Center',
                                                  command=self.click_iter)
        self.btn_close = ttk.Button(self.frm_cube_window, text='Close', command=self.close_window)
        self.lbl_img_desc = tk.Label(self.frm_cube_window, text='Load alignment, calibration, and offsets')
        self.lbl_img = tk.Label(self.frm_cube_window)
        # Place widgets within grid
        self.btn_load_alignment.grid(column=0, row=0, padx=5, pady=5)
        self.btn_measure_cube_center.grid(column=0, row=3, padx=5, pady=5)
        self.btn_close.grid(column=0, row=4, padx=5, pady=5)
        self.lbl_img_desc.grid(column=1, row=0, padx=5, pady=5, sticky='w')
        self.lbl_img.grid(column=1, row=1, rowspan=5, padx=5, pady=5)
    
    def load_alignment(self):
        self.cube_filename = filedialog.askopenfilename(filetypes=[('Text Files', '*.txt'), ('All Files', '*.*')])
        self.lbl_img.configure(image=self.images['x1'])
        self.lbl_img_desc.configure(text='Manually guide hallprobe into cube.')
        self.focus()
    
    def measure_origin(self):
        if self.cube is None:
            self.cube = Cube(self.cube_filename, self.calib_array, 'fsv_offset.txt')
            self.manual_position = self.cube.mcs2cube(self.cube.cmm.get_position())
            self.probe_offset_cube = self.cube.probe_offset@self.cube.rotation
            self.manual_origin_cube = np.array([self.manual_position[0], self.manual_position[1], self.probe_offset_cube[2]])
        if self.click_index < 12:
            self.cube.cmm.cnc_on()
            self.cube.cmm.set_speed((5,5,5))
            self.cube.cmm.goto_position(self.cube.cube2mcs(self.manual_origin_cube))
            while np.linalg.norm(self.manual_origin_cube - self.cube.mcs2cube(self.cube.cmm.get_position())) > 0.025:
                pass
            self.cube.measure(self.keys[self.click_index])
            self.cube.cmm.set_speed((20,20,20))
            self.cube.cmm.goto_position(self.cube.cube2mcs(self.manual_origin_cube + np.array([0, 0, 85])))
            self.cube.cmm.set_speed((70,70,70))
            self.cube.cmm.cnc_off()
            if self.click_index == 11:
                nominal_flux_density = 87.84 # mT
                magnetic_temp_coeff = -0.000043 # mT/degC
                calib_temp = 23.5 # degC
                field_cube_angle = 0.7 # deg
                cube_temp = self.cube.cmm.get_workpiece_temp()
                calib_magnitude_matrix = np.identity * (nominal_flux_density + magnetic_temp_coeff * (cube_temp - calib_temp))*np.cos(np.deg2rad(field_cube_angle))
                print(f'cube center data:\n{self.cube.cube_dict.values()}')
                avg_cube_meas = orthogonalize(np.array([i for i in self.cube.cube_dict.values()]))
                s_matrix_mcs = np.linalg.inv(avg_cube_meas)@calib_magnitude_matrix@self.cube.rotation
                np.save('sensitivity.npy', s_matrix_mcs, allow_pickle=False)
                self.lbl_img_desc.configure(text='Cube qualification complete.  Window can now be closed.')
                self.btn_measure_cube_center.configure(state='disabled')
            self.click_index += 1
        else:
            self.btn_measure_cube_center.configure(state='disabled')

    def click_iter(self):
        if self.click_index is None:
            self.click_index = 0
        self.measure_origin()
        if self.click_index < 12:
            self.update_step()
        
    def update_step(self):
        self.lbl_img.configure(image=self.images[self.keys[self.click_index]])
        self.lbl_img_desc.configure(text=f'Rotate cube to side number {self.cube_sequence[self.click_index]}')
    
    def close_window(self):
        if self.cube is not None:
            self.cube.shutdown()
        self.destroy()

if __name__ == '__main__':
    test = Cube(r'D:\CMM Programs\Cube Calibration v3\cube_alignment.txt',
                np.load('zg_calib_coeffs.npy'),
                'fsv_offset.txt')
    
    test.daq.start_hallsensor_task()
    sleep(1)
    test.daq.pulse()
    data = test.daq.read_hallsensor()[7500:15000]
    cal_data = calib_data(test.calib_coeffs, data)
    cal_mean = np.mean(cal_data, axis=0)
    # data_mean = np.mean(data, axis=0)
    with open('cube_data_2021-07-14.txt', 'a') as file:
        file.write(f'{cal_mean[0]} {cal_mean[1]} {cal_mean[2]}\n')
    print(f'Bxyz: {cal_mean}')
    print(f'Magnitude: {np.linalg.norm(cal_mean)}')
    test.shutdown()