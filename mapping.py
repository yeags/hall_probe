import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename
import numpy as np
from hallprobe import HallProbe

class MapFrames(tk.Frame):
    def __init__(self, parent):
        self.hp = None
        self.mapframes_parent = parent
        super().__init__(parent)
        self.density_list = ['0.1', '0.25', '0.5', '1.0', '2.0', 'full res']
        self.scan_direction_list = [['x', 'y'], ['y', 'z'], ['z', 'x']]
        self.frm_fm_buttons = tk.Frame(self)
        self.frm_scan_point = tk.Frame(self)
        self.frm_scan_line = tk.Frame(self)
        self.frm_scan_area_volume = tk.Frame(self)
        self.frm_fm_buttons.grid(column=0, row=0, sticky='nsew')
        self.create_fm_buttons()
        self.scan_point_widgets()
        self.scan_line_widgets()
        self.scan_area_volume_widgets()

    def close_mapping(self):
        if self.hp is not None:
            self.hp.shutdown()
    
    def create_fm_buttons(self):
        self.btn_load_part_alignment = ttk.Button(self.frm_fm_buttons, text='Load Part Alignment', command=self.load_part_alignment)
        self.btn_scan_point = ttk.Button(self.frm_fm_buttons, text='Scan Point', state='disabled', command=lambda: self.load_frame(self.frm_scan_point))
        self.btn_scan_line = ttk.Button(self.frm_fm_buttons, text='Scan Line', state='disabled', command=lambda: self.load_frame(self.frm_scan_line))
        self.btn_scan_area_volume = ttk.Button(self.frm_fm_buttons, text='Scan Area/Volume', state='disabled', command=lambda: self.load_frame(self.frm_scan_area_volume))
        # Place widgets within grid
        self.btn_load_part_alignment.grid(column=0, row=0, sticky='new', padx=5, pady=5)
        self.btn_scan_point.grid(column=0, row=1, sticky='new', padx=5, pady=(0,5))
        self.btn_scan_line.grid(column=0, row=2, sticky='new', padx=5, pady=(0,5))
        self.btn_scan_area_volume.grid(column=0, row=3, sticky='new', padx=5, pady=(0,5))

    def get_point(self):
        x = float(self.ent_sp_x.get())
        y = float(self.ent_sp_y.get())
        z = float(self.ent_sp_z.get())
        point = self.hp.pcs2mcs(np.array([x, y, z]))
        return point

    def get_line(self):
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

    def get_area_volume(self):
        sp_x = float(self.ent_sav_sp_x.get())
        sp_y = float(self.ent_sav_sp_y.get())
        sp_z = float(self.ent_sav_sp_z.get())
        sd_x = float(self.ent_sav_sd_x.get())
        sd_y = float(self.ent_sav_sd_y.get())
        sd_z = float(self.ent_sav_sd_z.get())
        pd = float(self.cbox_sav_pd.get())
        scan_plane = self.cbox_sav_scan_plane.get()
        scan_direction = self.cbox_sav_scan_direction.get()
        start_point = self.hp.pcs2mcs(np.array([sp_x, sp_y, sp_z]))
        scan_distance = np.array([sd_x, sd_y, sd_z])@self.hp.rotation
        return (start_point, scan_distance, pd, scan_plane, scan_direction)
    
    def load_frame(self, frame: tk.Frame):
        if self.grid_slaves(column=1, row=0):
            self.grid_slaves()[0].grid_forget()
        frame.grid(column=1, row=0, sticky='nsew')

    def load_part_alignment(self):
        cdiff = askopenfilename(filetypes=[('Text Files', '*.txt'), ('All Files', '*.*')])
        if cdiff != '':
            self.hp = HallProbe(cdiff, 1, 2)
            self.btn_scan_point.configure(state='enabled')
            self.btn_scan_line.configure(state='enabled')
            self.btn_scan_area_volume.configure(state='enabled')
    
    def measure_point(self):
        point = self.get_point()
        xyz_Bxyz = self.hp.scan_point(point)
        xyz_Bxyz[:3] = self.hp.mcs2pcs(xyz_Bxyz[:3])
        xyz_Bxyz[3:] = xyz_Bxyz[3:]@np.linalg.inv(self.hp.rotation)
        print(xyz_Bxyz)
    
    def measure_line(self):
        line_args = self.get_line()
        data = self.hp.scan_line(*line_args)
        for i, sample in enumerate(data):
            data[i, :3] = self.hp.mcs2pcs(data[i, :3])
            data[i, 3:] = data[i, 3:]@np.linalg.inv(self.hp.rotation)
        print(data.shape)

    def measure_area_volume(self):
        sav_args = self.get_area_volume()
        data = self.hp.scan_area_volume(*sav_args)

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
        if self.cbox_sav_scan_plane.get() == 'xy':
            self.cbox_sav_scan_direction.configure(values=self.scan_direction_list[0])
            self.cbox_sav_scan_direction.set('x')
        elif self.cbox_sav_scan_plane.get() == 'yz':
            self.cbox_sav_scan_direction.configure(values=self.scan_direction_list[1])
            self.cbox_sav_scan_direction.set('y')
        elif self.cbox_sav_scan_plane.get() == 'zx':
            self.cbox_sav_scan_direction.configure(values=self.scan_direction_list[2])
            self.cbox_sav_scan_direction.set('z')

    def scan_area_volume_widgets(self):
        self.lbl_sav_sp = tk.Label(self.frm_scan_area_volume, text='Start Point')
        self.lbl_sav_sp_x = tk.Label(self.frm_scan_area_volume, text='X')
        self.lbl_sav_sp_y = tk.Label(self.frm_scan_area_volume, text='Y')
        self.lbl_sav_sp_z = tk.Label(self.frm_scan_area_volume, text='Z')
        self.lbl_sav_distance = tk.Label(self.frm_scan_area_volume, text='Scan Distance')
        self.lbl_sav_sd_x = tk.Label(self.frm_scan_area_volume, text='X')
        self.lbl_sav_sd_y = tk.Label(self.frm_scan_area_volume, text='Y')
        self.lbl_sav_sd_z = tk.Label(self.frm_scan_area_volume, text='Z')
        self.ent_sav_sp_x = ttk.Entry(self.frm_scan_area_volume, width=9)
        self.ent_sav_sp_y = ttk.Entry(self.frm_scan_area_volume, width=9)
        self.ent_sav_sp_z = ttk.Entry(self.frm_scan_area_volume, width=9)
        self.ent_sav_sd_x = ttk.Entry(self.frm_scan_area_volume, width=9)
        self.ent_sav_sd_y = ttk.Entry(self.frm_scan_area_volume, width=9)
        self.ent_sav_sd_z = ttk.Entry(self.frm_scan_area_volume, width=9)
        self.lbl_sav_pd = tk.Label(self.frm_scan_area_volume, text='Point Density')
        self.cbox_sav_pd = ttk.Combobox(self.frm_scan_area_volume, values=self.density_list, width=9)
        self.lbl_sav_scan_plane = tk.Label(self.frm_scan_area_volume, text='Scan Plane')
        self.lbl_sav_scan_direction = tk.Label(self.frm_scan_area_volume, text='Scan Direction')
        self.cbox_sav_scan_plane = ttk.Combobox(self.frm_scan_area_volume, values=['xy', 'yz', 'zx'], state='readonly', width=9)
        self.cbox_sav_scan_direction = ttk.Combobox(self.frm_scan_area_volume, values=self.scan_direction_list[0], state='readonly', width=9)
        self.btn_sav_measure = ttk.Button(self.frm_scan_area_volume, text='Measure', command=self.measure_area_volume)
        self.btn_sav_stop = ttk.Button(self.frm_scan_area_volume, text='Stop')
        # Place widgets within grid
        self.lbl_sav_sp.grid(column=0, row=0, columnspan=6)
        self.lbl_sav_sp_x.grid(column=0, row=1, sticky='e')
        self.lbl_sav_sp_y.grid(column=2, row=1, sticky='e')
        self.lbl_sav_sp_z.grid(column=4, row=1, sticky='e')
        self.ent_sav_sp_x.grid(column=1, row=1, padx=(5,10), sticky='w')
        self.ent_sav_sp_y.grid(column=3, row=1, padx=(5,10), sticky='w')
        self.ent_sav_sp_z.grid(column=5, row=1, padx=(5,10), sticky='w')
        self.lbl_sav_distance.grid(column=0, row=2, columnspan=6)
        self.lbl_sav_sd_x.grid(column=0, row=3, sticky='e')
        self.lbl_sav_sd_y.grid(column=2, row=3, sticky='e')
        self.lbl_sav_sd_z.grid(column=4, row=3, sticky='e')
        self.ent_sav_sd_x.grid(column=1, row=3, padx=(5,10), sticky='w')
        self.ent_sav_sd_y.grid(column=3, row=3, padx=(5,10), sticky='w')
        self.ent_sav_sd_z.grid(column=5, row=3, padx=(5,10), sticky='w')
        self.lbl_sav_pd.grid(column=0, row=4, columnspan=2, pady=(10,5), sticky='e')
        self.cbox_sav_pd.grid(column=2, row=4, columnspan=2, padx=5, pady=(10,5), sticky='w')
        self.cbox_sav_pd.set('0.5')
        self.lbl_sav_scan_plane.grid(column=0, row=5, columnspan=2, pady=(0,5), sticky='e')
        self.cbox_sav_scan_plane.grid(column=2, row=5, columnspan=2, padx=5, pady=(0,5), sticky='w')
        self.cbox_sav_scan_plane.set('xy')
        self.cbox_sav_scan_plane.bind('<<ComboboxSelected>>', self.update_cbox)
        self.lbl_sav_scan_direction.grid(column=0, row=6, columnspan=2, pady=(0,5), sticky='e')
        self.cbox_sav_scan_direction.grid(column=2, row=6, columnspan=2, padx=5, pady=(0,5), sticky='w')
        self.cbox_sav_scan_direction.set('x')
        self.btn_sav_measure.grid(column=4, row=5, columnspan=2, padx=5, pady=(5,0), sticky='ew')
        self.btn_sav_stop.grid(column=4, row=6, columnspan=2, padx=5, pady=(0,5), sticky='ew')

if __name__ == '__main__':
    test = tk.Tk()
    mf = MapFrames(test)
    mf.pack()
    test.mainloop()