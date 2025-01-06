import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showerror
import numpy as np
from hallprobe import HallProbe
import pickle
import os

class MapFrames(tk.Frame):
    def __init__(self, parent):
        self.hp = None
        self.mapframes_parent = parent
        super().__init__(parent)
        self.density_list = ['0.1', '0.25', '0.5', '1.0', '2.0', 'full res']
        self.density_list_area = ['0.1', '0.25', '0.5', '1.0', '2.0']
        self.scan_direction_list = [['x', 'y'], ['y', 'z'], ['z', 'x']]
        self.frm_fm_buttons = tk.Frame(self)
        self.frm_scan_point = tk.Frame(self)
        self.frm_scan_line = tk.Frame(self)
        self.frm_scan_area = tk.Frame(self)
        self.frm_fm_buttons.grid(column=0, row=0, sticky='nsew')
        self.create_fm_buttons()
        self.scan_point_widgets()
        self.scan_line_widgets()
        self.scan_area_widgets()

    def close_mapping(self):
        if self.hp is not None:
            self.hp.shutdown()
    
    def create_fm_buttons(self):
        self.btn_load_part_alignment = ttk.Button(self.frm_fm_buttons, text='Load Part Alignment', command=self.load_part_alignment)
        self.btn_scan_point = ttk.Button(self.frm_fm_buttons, text='Scan Point', state='disabled', command=lambda: self.load_frame(self.frm_scan_point))
        self.btn_scan_line = ttk.Button(self.frm_fm_buttons, text='Scan Line', state='disabled', command=lambda: self.load_frame(self.frm_scan_line))
        self.btn_scan_area_volume = ttk.Button(self.frm_fm_buttons, text='Scan Area', state='disabled', command=lambda: self.load_frame(self.frm_scan_area))
        # Place widgets within grid
        self.btn_load_part_alignment.grid(column=0, row=0, sticky='new', padx=5, pady=5)
        self.btn_scan_point.grid(column=0, row=1, sticky='new', padx=5, pady=(0,5))
        self.btn_scan_line.grid(column=0, row=2, sticky='new', padx=5, pady=(0,5))
        self.btn_scan_area_volume.grid(column=0, row=3, sticky='new', padx=5, pady=(0,5))

    def load_magnet_info(self):
        # grab from pickled file
        # entries are in a list ['magnet name', 'serial number', 'current', 'notes']
        with open('magnet_info.pkl', 'rb') as f:
            magnet_info = pickle.load(f)
        return magnet_info
    
    def get_point(self):
        try:
            x = float(self.ent_sp_x.get())
            y = float(self.ent_sp_y.get())
            z = float(self.ent_sp_z.get())
            point = np.array([x, y, z])
            return point
        except ValueError:
            return None

    def get_line(self):
        try:
            sp_x = float(self.ent_slsp_x.get())
            sp_y = float(self.ent_slsp_y.get())
            sp_z = float(self.ent_slsp_z.get())
            ep_x = float(self.ent_slep_x.get())
            ep_y = float(self.ent_slep_y.get())
            ep_z = float(self.ent_slep_z.get())
            sp = self.hp.pcs2mcs(np.array([sp_x, sp_y, sp_z]))
            ep = self.hp.pcs2mcs(np.array([ep_x, ep_y, ep_z]))
            pd = self.cbox_sl_point_density.get()
            if pd == 'full res':
                pass
            else:
                pd = float(pd)
            return (sp, ep, pd)
        except ValueError:
            return None

    def get_area(self):
        try:
            sp_x = float(self.ent_sa_sp_x.get())
            sp_y = float(self.ent_sa_sp_y.get())
            sp_z = float(self.ent_sa_sp_z.get())
            sd_x = float(self.ent_sa_sd_x.get())
            sd_y = float(self.ent_sa_sd_y.get())
            sd_z = float(self.ent_sa_sd_z.get())
            pd = float(self.cbox_sa_pd.get())
            print(f'sp_x: {sp_x}')
            scan_plane = self.cbox_sa_scan_plane.get()
            scan_direction = self.cbox_sa_scan_direction.get()
            start_point = np.array([sp_x, sp_y, sp_z])
            scan_distance = np.array([sd_x, sd_y, sd_z])
            start_array = self.hp.create_scan_plane(start_point, scan_distance, pd, scan_plane, scan_direction)
            distance_dict = {'x': sd_x, 'y': sd_y, 'z': sd_z}
            for i, point in enumerate(start_array):
                start_array[i] = self.hp.pcs2mcs(point)
            distance = distance_dict[scan_direction]
            travel_time = distance / self.hp.scan_speed
            samples = np.array(((travel_time * self.hp.sample_rate) - self.hp.sample_rate)).round(0).astype(int)
            allocated_array = np.zeros((start_array.shape[0], samples, 6))
            return (start_array, allocated_array, pd, samples, scan_direction)
        except ValueError:
            return None
    
    def load_frame(self, frame: tk.Frame):
        if self.grid_slaves(column=1, row=0):
            self.grid_slaves()[0].grid_forget()
        frame.grid(column=1, row=0, sticky='nsew')

    def load_part_alignment(self):
        cdiff = askopenfilename(filetypes=[('Text Files', '*.txt'), ('All Files', '*.*')])
        if cdiff != '' and self.hp is None:
            self.hp = HallProbe(cdiff, 1, 2)
            self.btn_scan_point.configure(state='enabled')
            self.btn_scan_line.configure(state='enabled')
            self.btn_scan_area_volume.configure(state='enabled')
        elif cdiff != '' and self.hp is not None:
            self.hp.__load_coord_diff__(cdiff)
    
    def measure_point(self):
        point = self.get_point()
        magnet_info = self.load_magnet_info()
        magname, serial, current, notes = magnet_info
        mag_folder = f'scans/{magname}-{serial}/'
        filename = f'{magname}-{serial} points.txt'
        # Create a subdirectory within the scans folder for the magnet only if it doesn't already exist
        if not os.path.exists(mag_folder):
            os.makedirs(mag_folder)
        # Verify entries are valid
        if point is None:
            showerror(title='Entry Error', message='Entries should be integer or float values.')
        else:
            xyz_Bxyz = self.hp.scan_point(point)
            # Transform xyz to PCS
            xyz_Bxyz[:3] = self.hp.mcs2pcs(xyz_Bxyz[:3])
            with open(mag_folder + magname + '-' + serial + ' points Bxyz raw.txt', 'a') as raw_file:
                raw_file.write(f'{xyz_Bxyz[0]} {xyz_Bxyz[1]} {xyz_Bxyz[2]} {xyz_Bxyz[3]} {xyz_Bxyz[4]} {xyz_Bxyz[5]}\n')
            # Transform Bxyz to PCS
            #xyz_Bxyz[3:] = xyz_Bxyz[3:] @ self.hp.s_matrix @ self.hp.rotation
            corr=np.array([[1, 0, 0], [0, 1, -0.00], [0, 0, 1]]) # Overhearing value found on ABEND-35 on date 2024-08-21.
            xyz_Bxyz[3:] = xyz_Bxyz[3:] @ self.hp.s_matrix @ self.hp.rotation @ corr
            # Print xyz and Bxyz wrt PCS
            print(f'x {xyz_Bxyz[0]} y {xyz_Bxyz[1]} z {xyz_Bxyz[2]} Bx {xyz_Bxyz[3]} By {xyz_Bxyz[4]} Bz {xyz_Bxyz[5]}')
            # Save xyz and Bxyz values wrt PCS
            with open(mag_folder+filename, 'a') as file:
                file.write(f'{xyz_Bxyz[0]} {xyz_Bxyz[1]} {xyz_Bxyz[2]} {xyz_Bxyz[3]} {xyz_Bxyz[4]} {xyz_Bxyz[5]}\n')
    
    def measure_line(self):
        line_args = self.get_line()
        magnet_info = self.load_magnet_info()
        magname, serial, current, notes = magnet_info
        mag_folder = f'scans/{magname}-{serial}/'
        filename = f'{magname}-{serial} line data.txt'
        # Create a subdirectory within the scans folder for the magnet only if it doesn't already exist
        if not os.path.exists(mag_folder):
            os.makedirs(mag_folder)
        # Verify entries are valid and scan line
        if line_args is None:
            showerror(title='Entry Error', message='Entries should be integer or float values.')
        else:
            data = self.hp.scan_line(*line_args)
            data_xyz_pcs = np.array([self.hp.mcs2pcs(i) for i in data[:, :3]])
            data_raw = np.hstack((data_xyz_pcs, data[:, 3:]))
            np.savetxt('line_data_raw_Bxyz.txt', data_raw, delimiter=' ', fmt='%.3f')
            for i, sample in enumerate(data):
                data[i, :3] = self.hp.mcs2pcs(data[i, :3])
                #data[i, 3:] = data[i, 3:] @ self.hp.s_matrix @ self.hp.rotation
                corr=np.array([[1, 0, 0], [0, 1, -0.00], [0, 0, 1]]) # Overhearing value found on ABEND-35 on date 2024-08-21.
                data[i, 3:] = data[i, 3:] @ self.hp.s_matrix @ self.hp.rotation @ corr
            np.save(mag_folder + f'{magname}-{serial} line.npy', data, allow_pickle=False)
            np.savetxt(mag_folder + filename, data, delimiter=' ', fmt='%.3f')

    def measure_area(self):
        sa_args = self.get_area()
        magnet_info = self.load_magnet_info()
        magname, serial, current, notes = magnet_info
        mag_folder = f'scans/{magname}-{serial}/'
        filename = f'{magname}-{serial} area data.txt'
        if not os.path.exists(mag_folder):
            os.makedirs(mag_folder)
        if sa_args is None:
            showerror(title='Entry Error', message='Entries should be integer or float values.')
        else:
            data, filtered_array = self.hp.scan_area(*sa_args)
            print(f'Raw data shape: {data.shape}')
            print(f'Filtered data shape: {filtered_array.shape}')
            print(f'Raw data type: {type(data)}')
            print(f'Filtered data type: {type(filtered_array)}')
            np.save(mag_folder + f'{magname}-{serial} raw area data.npy', data)
            # Reshape array to shape (m*n, 6)
            data_2d = data.reshape((data.shape[0]*data.shape[1], data.shape[2]))
            filtered_array_2d = filtered_array.reshape((filtered_array.shape[0]*filtered_array.shape[1], filtered_array.shape[2]))
            for i, point in enumerate(filtered_array_2d):
                filtered_array_2d[i, :3] = self.hp.mcs2pcs(point[:3])
                filtered_array_2d[i, 3:] = point[3:] @ self.hp.s_matrix @ self.hp.rotation
            for i, point in enumerate(data_2d):
                data_2d[i, :3] = self.hp.mcs2pcs(point[:3])
                #dat   a_2d[i, 3:] = point[3:] @ self.hp.s_matrix @ self.hp.rotation
                corr=np.array([[1, 0, 0], [0, 1, -0.00], [0, 0, 1]]) # Overhearing value found on ABEND-35 on date 2024-08-21.
                data_2d[i, 3:] = point[3:] @ self.hp.s_matrix @ self.hp.rotation @ corr
            np.savetxt(mag_folder + filename, data_2d, delimiter=' ', fmt='%.3f')
            np.savetxt(mag_folder + f'{magname}-{serial} area full res lines.txt', filtered_array_2d, delimiter=' ', fmt='%.3f')

    def scan_point_widgets(self):
        self.lbl_scan_point = tk.Label(self.frm_scan_point, text='Scan Point')
        self.lbl_sp_x = tk.Label(self.frm_scan_point, text='X')
        self.lbl_sp_y = tk.Label(self.frm_scan_point, text='Y')
        self.lbl_sp_z = tk.Label(self.frm_scan_point, text='Z')
        self.ent_sp_x = ttk.Entry(self.frm_scan_point, width=9)
        self.ent_sp_y = ttk.Entry(self.frm_scan_point, width=9)
        self.ent_sp_z = ttk.Entry(self.frm_scan_point, width=9)
        self.btn_measure_point = ttk.Button(self.frm_scan_point, text='Measure', command=self.measure_point)
        # Place widgets within grid
        self.lbl_scan_point.grid(column=0, row=0, columnspan=6)
        self.lbl_sp_x.grid(column=0, row=1, sticky='e')
        self.lbl_sp_y.grid(column=2, row=1, sticky='e')
        self.lbl_sp_z.grid(column=4, row=1, sticky='e')
        self.ent_sp_x.grid(column=1, row=1, sticky='w', padx=(5,10))
        self.ent_sp_y.grid(column=3, row=1, sticky='w', padx=(5,10))
        self.ent_sp_z.grid(column=5, row=1, sticky='w', padx=(5,10))
        self.btn_measure_point.grid(column=0, row=2, columnspan=6, padx=5, pady=5)

    def scan_line_widgets(self):
        self.lbl_start_point = tk.Label(self.frm_scan_line, text='Start Point')
        self.lbl_slsp_x = tk.Label(self.frm_scan_line, text='X')
        self.lbl_slsp_y = tk.Label(self.frm_scan_line, text='Y')
        self.lbl_slsp_z = tk.Label(self.frm_scan_line, text='Z')
        self.lbl_end_point = tk.Label(self.frm_scan_line, text='End Point')
        self.lbl_slep_x = tk.Label(self.frm_scan_line, text='X')
        self.lbl_slep_y = tk.Label(self.frm_scan_line, text='Y')
        self.lbl_slep_z = tk.Label(self.frm_scan_line, text='Z')
        self.lbl_point_density = tk.Label(self.frm_scan_line, text='Point Density')
        self.ent_slsp_x = ttk.Entry(self.frm_scan_line, width=9)
        self.ent_slsp_y = ttk.Entry(self.frm_scan_line, width=9)
        self.ent_slsp_z = ttk.Entry(self.frm_scan_line, width=9)
        self.ent_slep_x = ttk.Entry(self.frm_scan_line, width=9)
        self.ent_slep_y = ttk.Entry(self.frm_scan_line, width=9)
        self.ent_slep_z = ttk.Entry(self.frm_scan_line, width=9)
        self.cbox_sl_point_density = ttk.Combobox(self.frm_scan_line, values=self.density_list, width=9)
        self.btn_measure_line = ttk.Button(self.frm_scan_line, text='Measure', command=self.measure_line)
        # Place widgets within grid
        self.lbl_start_point.grid(column=0, row=0, columnspan=6)
        self.lbl_slsp_x.grid(column=0, row=1, sticky='e')
        self.lbl_slsp_y.grid(column=2, row=1, sticky='e')
        self.lbl_slsp_z.grid(column=4, row=1, sticky='e')
        self.ent_slsp_x.grid(column=1, row=1, sticky='w', padx=(5,10))
        self.ent_slsp_y.grid(column=3, row=1, sticky='w', padx=(5,10))
        self.ent_slsp_z.grid(column=5, row=1, sticky='w', padx=(5,10))
        self.lbl_end_point.grid(column=0, row=6, columnspan=6)
        self.lbl_slep_x.grid(column=0, row=7, sticky='e')
        self.lbl_slep_y.grid(column=2, row=7, sticky='e')
        self.lbl_slep_z.grid(column=4, row=7, sticky='e')
        self.ent_slep_x.grid(column=1, row=7, sticky='w', padx=(5,10))
        self.ent_slep_y.grid(column=3, row=7, sticky='w', padx=(5,10))
        self.ent_slep_z.grid(column=5, row=7, sticky='w', padx=(5,10))
        self.lbl_point_density.grid(column=0, row=8, columnspan=2, sticky='e')
        self.cbox_sl_point_density.grid(column=2, row=8, columnspan=2, sticky='w', padx=5, pady=5)
        self.cbox_sl_point_density.set('full res')
        self.btn_measure_line.grid(column=4, row=8, columnspan=2)
    
    def update_cbox(self, event):
        if self.cbox_sa_scan_plane.get() == 'xy':
            self.__enable_ent_sd__()
            self.ent_sa_sd_z.delete(0, tk.END)
            self.ent_sa_sd_z.insert(tk.END, '0')
            self.cbox_sa_scan_direction.configure(values=self.scan_direction_list[0])
            self.cbox_sa_scan_direction.set('x')
            self.ent_sa_sd_z.configure(state='disabled')
        elif self.cbox_sa_scan_plane.get() == 'yz':
            self.__enable_ent_sd__()
            self.ent_sa_sd_x.delete(0, tk.END)
            self.ent_sa_sd_x.insert(tk.END, '0')
            self.cbox_sa_scan_direction.configure(values=self.scan_direction_list[1])
            self.cbox_sa_scan_direction.set('y')
            self.ent_sa_sd_x.configure(state='disabled')
        elif self.cbox_sa_scan_plane.get() == 'zx':
            self.__enable_ent_sd__()
            self.ent_sa_sd_y.delete(0, tk.END)
            self.ent_sa_sd_y.insert(tk.END, '0')
            self.cbox_sa_scan_direction.configure(values=self.scan_direction_list[2])
            self.cbox_sa_scan_direction.set('z')
            self.ent_sa_sd_y.configure(state='disabled')
    
    def __enable_ent_sd__(self):
        self.ent_sa_sd_x.configure(state='enabled')
        self.ent_sa_sd_y.configure(state='enabled')
        self.ent_sa_sd_z.configure(state='enabled')

    def scan_area_widgets(self):
        self.lbl_sa_sp = tk.Label(self.frm_scan_area, text='Start Point')
        self.lbl_sa_sp_x = tk.Label(self.frm_scan_area, text='X')
        self.lbl_sa_sp_y = tk.Label(self.frm_scan_area, text='Y')
        self.lbl_sa_sp_z = tk.Label(self.frm_scan_area, text='Z')
        self.lbl_sa_distance = tk.Label(self.frm_scan_area, text='Scan Distance')
        self.lbl_sa_sd_x = tk.Label(self.frm_scan_area, text='X')
        self.lbl_sa_sd_y = tk.Label(self.frm_scan_area, text='Y')
        self.lbl_sa_sd_z = tk.Label(self.frm_scan_area, text='Z')
        self.ent_sa_sp_x = ttk.Entry(self.frm_scan_area, width=9)
        self.ent_sa_sp_y = ttk.Entry(self.frm_scan_area, width=9)
        self.ent_sa_sp_z = ttk.Entry(self.frm_scan_area, width=9)
        self.ent_sa_sd_x = ttk.Entry(self.frm_scan_area, width=9)
        self.ent_sa_sd_y = ttk.Entry(self.frm_scan_area, width=9)
        self.ent_sa_sd_z = ttk.Entry(self.frm_scan_area, width=9)
        self.lbl_sa_pd = tk.Label(self.frm_scan_area, text='Point Density')
        self.cbox_sa_pd = ttk.Combobox(self.frm_scan_area, values=self.density_list_area, width=9)
        self.lbl_sa_scan_plane = tk.Label(self.frm_scan_area, text='Scan Plane')
        self.lbl_sa_scan_direction = tk.Label(self.frm_scan_area, text='Scan Direction')
        self.cbox_sa_scan_plane = ttk.Combobox(self.frm_scan_area, values=['xy', 'yz', 'zx'], state='readonly', width=9)
        self.cbox_sa_scan_direction = ttk.Combobox(self.frm_scan_area, values=self.scan_direction_list[0], state='readonly', width=9)
        self.btn_sa_measure = ttk.Button(self.frm_scan_area, text='Measure', command=self.measure_area)
        self.btn_sa_stop = ttk.Button(self.frm_scan_area, text='Stop')
        # Place widgets within grid
        self.lbl_sa_sp.grid(column=0, row=0, columnspan=6)
        self.lbl_sa_sp_x.grid(column=0, row=1, sticky='e')
        self.lbl_sa_sp_y.grid(column=2, row=1, sticky='e')
        self.lbl_sa_sp_z.grid(column=4, row=1, sticky='e')
        self.ent_sa_sp_x.grid(column=1, row=1, padx=(5,10), sticky='w')
        self.ent_sa_sp_y.grid(column=3, row=1, padx=(5,10), sticky='w')
        self.ent_sa_sp_z.grid(column=5, row=1, padx=(5,10), sticky='w')
        self.lbl_sa_distance.grid(column=0, row=2, columnspan=6)
        self.lbl_sa_sd_x.grid(column=0, row=3, sticky='e')
        self.lbl_sa_sd_y.grid(column=2, row=3, sticky='e')
        self.lbl_sa_sd_z.grid(column=4, row=3, sticky='e')
        self.ent_sa_sd_x.grid(column=1, row=3, padx=(5,10), sticky='w')
        self.ent_sa_sd_y.grid(column=3, row=3, padx=(5,10), sticky='w')
        self.ent_sa_sd_z.grid(column=5, row=3, padx=(5,10), sticky='w')
        self.lbl_sa_pd.grid(column=0, row=4, columnspan=2, pady=(10,5), sticky='e')
        self.cbox_sa_pd.grid(column=2, row=4, columnspan=2, padx=5, pady=(10,5), sticky='w')
        self.cbox_sa_pd.set('1.0')
        self.lbl_sa_scan_plane.grid(column=0, row=5, columnspan=2, pady=(0,5), sticky='e')
        self.cbox_sa_scan_plane.grid(column=2, row=5, columnspan=2, padx=5, pady=(0,5), sticky='w')
        self.cbox_sa_scan_plane.set('xy')
        self.ent_sa_sd_z.insert(tk.END, '0')
        self.ent_sa_sd_z.configure(state='disabled')
        self.cbox_sa_scan_plane.bind('<<ComboboxSelected>>', self.update_cbox)
        self.lbl_sa_scan_direction.grid(column=0, row=6, columnspan=2, pady=(0,5), sticky='e')
        self.cbox_sa_scan_direction.grid(column=2, row=6, columnspan=2, padx=5, pady=(0,5), sticky='w')
        self.cbox_sa_scan_direction.set('x')
        self.btn_sa_measure.grid(column=4, row=5, columnspan=2, padx=5, pady=(5,0), sticky='ew')
        self.btn_sa_stop.grid(column=4, row=6, columnspan=2, padx=5, pady=(0,5), sticky='ew')

if __name__ == '__main__':
    test = tk.Tk()
    mf = MapFrames(test)
    mf.pack()
    test.mainloop()