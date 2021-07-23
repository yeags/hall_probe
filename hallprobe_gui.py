import tkinter as tk
from tkinter import ttk
from tkinter.constants import W
from tkinter.messagebox import showinfo
from tkinter.scrolledtext import ScrolledText
from zeisscmm import CMM
from fsv import fsvWindow
from cube import CubeWindow
from zero_gauss import zgWindow
import numpy as np
from os.path import isfile

import matplotlib
matplotlib.use("TkAgg")
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

from tooltip import ToolTip

class HallProbeApp(tk.Frame):
    '''
    Master tk frame to place all containers in.
    '''
    def __init__(self, master):
        self.master = master
        super().__init__(master)
        # self.master.resizable(0,0)
        # self.master.columnconfigure(0, weight=1)
        # self.master.rowconfigure(0, weight=1)
        self.master.title('Hall Probe CMM Program')
        self.master.iconbitmap('magnet.ico')
        self.master.geometry('1350x900')
        self.create_frames()
    
    def create_frames(self):
        self.controls = ControlsFrame(self)
        self.visuals = VisualsFrame(self)
        self.grid(column=0, row=0, sticky='nsew')
        # self.columnconfigure(0, weight=1)
        # self.rowconfigure(0, weight=1)
        self.controls.grid(column=0, row=0, padx=5, pady=5, sticky='nsew')
        self.visuals.grid(column=1, row=0, padx=(0,5), pady=(5,0), sticky='nsew')
        # self.controls.columnconfigure(0, weight=1)
        # self.visuals.columnconfigure(1, weight=1)
        # self.controls.rowconfigure(0, weight=1)
        # self.visuals.rowconfigure(0, weight=1)
    
    def update_graph_labels(self):
        self.visuals.temp_plot.temp_frame_parent.temp_plot.update_labels()
    
    def on_closing(self):
        if tk.messagebox.askokcancel('Quit', 'Do you want to quit?'):
            self.master.destroy()

class ControlsFrame(tk.Frame):
    '''
    Parent tk frame for inputs, parameters, and controls options.
    '''
    def __init__(self, parent):
        self.controls_frame_parent = parent
        super().__init__(parent)
        self.create_frames()
    
    def create_frames(self):
        self.magnet_info_frame = MagnetInformation(self)
        self.map_field_frame = MapField(self)
        self.calibration_frame = ProbeQualification(self)
        self.program_frame = ProgramControls(self)

        self.magnet_info_frame.grid(column=0, row=0, sticky='nsew')
        self.calibration_frame.grid(column=0, row=1, pady=(10,0), sticky='nsew')
        self.map_field_frame.grid(column=0, row=2, sticky='nsew')
        self.program_frame.grid(column=0, row=3, sticky='nsew')

class VisualsFrame(tk.Frame):
    '''
    Parent tk frame for graphical plots.
    '''
    def __init__(self, parent):
        self.visuals_frame_parent = parent
        super().__init__(parent)
        self.create_frames()

    def create_frames(self):
        self.field_plot = FieldFrame(self)
        self.temp_plot = TemperatureFrame(self)
        self.field_plot.grid(column=0, row=0)
        self.temp_plot.grid(column=0, row=1)

class MagnetInformation(ttk.LabelFrame):
    '''
    tk frame for part identification
    '''
    def __init__(self, parent, title='Magnet Information'):
        self.magnet_info_parent = parent
        super().__init__(parent, text=title, labelanchor='nw')
        self.create_widgets()

    def create_widgets(self):
        self.lbl_partnum = tk.Label(self, text='Part Number')
        self.lbl_serial = tk.Label(self, text='Serial Number')
        self.lbl_notes = tk.Label(self, text='Notes')
        self.ent_partnum = ttk.Entry(self)
        self.ent_serial = ttk.Entry(self)
        self.txt_notes = ScrolledText(self, width=60, height=12)
        # Place widgets within grid
        self.lbl_partnum.grid(column=0, row=0, sticky='w', padx=5)
        self.lbl_serial.grid(column=1, row=0, sticky='w', padx=5)
        self.lbl_notes.grid(column=0, row=2, sticky='w', padx=5, pady=(5,0))
        self.ent_partnum.grid(column=0, row=1, sticky='w', padx=5, pady=(0,5))
        self.ent_serial.grid(column=1, row=1, sticky='w', padx=5, pady=(0,5))
        self.txt_notes.grid(column=0, row=3, columnspan=2, sticky='nw', padx=5, pady=(0,5))

class MapField(ttk.LabelFrame):
    '''
    tk frame for inputting CMM parameters such as
    starting coordinate, scan length, speed, and measurement interval
    '''
    def __init__(self, parent, title='Field Mapping'):
        self.map_field_parent = parent
        super().__init__(parent, text=title, labelanchor='nw')
        self.grid(pady=10, sticky='nsew')
        self.create_frames()
        self.create_widgets()

    def create_frames(self):
        self.frm_buttons = tk.Frame(self)
        self.frm_start_point = tk.Frame(self)
        self.frm_scan_volume = tk.Frame(self)
        self.frm_parameters = tk.Frame(self)

        self.frm_buttons.grid(column=0, row=0, rowspan=3, padx=(0, 10), sticky='new')
        self.frm_start_point.grid(column=1, row=0, sticky='new')
        self.frm_scan_volume.grid(column=1, row=1, sticky='new')
        self.frm_parameters.grid(column=1, row=2, sticky='new')
    
    def create_widgets(self):
        self.btn_load_part_alignment = ttk.Button(self.frm_buttons, text='Load Part Alignment')
        self.btn_scan_point = ttk.Button(self.frm_buttons, text='Scan Point')
        self.btn_scan_line = ttk.Button(self.frm_buttons, text='Scan Line')
        self.btn_run_pause = ttk.Button(self.frm_buttons, text='Scan Area/Volume')
        self.btn_stop_mapping = ttk.Button(self.frm_buttons, text='Stop')
        self.lbl_start_point = tk.Label(self.frm_start_point, text='Start Point')
        self.lbl_scan_volume = tk.Label(self.frm_scan_volume, text='Scan Area/Volume')
        self.lbl_sampling_interval = tk.Label(self.frm_parameters, text='Sampling Interval')
        self.lbl_scanning_plane = tk.Label(self.frm_parameters, text='Scanning Plane')
        self.lbl_scanning_plane_interval = tk.Label(self.frm_parameters, text='Plane Interval')
        self.lbl_sp_x = tk.Label(self.frm_start_point, text='X')
        self.lbl_sp_y = tk.Label(self.frm_start_point, text='Y')
        self.lbl_sp_z = tk.Label(self.frm_start_point, text='Z')
        self.lbl_sv_x = tk.Label(self.frm_scan_volume, text='X')
        self.lbl_sv_y = tk.Label(self.frm_scan_volume, text='Y')
        self.lbl_sv_z = tk.Label(self.frm_scan_volume, text='Z')
        self.ent_start_pt_x = ttk.Entry(self.frm_start_point, width=9)
        self.ent_start_pt_y = ttk.Entry(self.frm_start_point, width=9)
        self.ent_start_pt_z = ttk.Entry(self.frm_start_point, width=9)
        self.ent_scan_volume_x = ttk.Entry(self.frm_scan_volume, width=9)
        self.ent_scan_volume_y = ttk.Entry(self.frm_scan_volume, width=9)
        self.ent_scan_volume_z = ttk.Entry(self.frm_scan_volume, width=9)
        self.ent_sampling_interval = ttk.Entry(self.frm_parameters, width=9)
        self.ent_scan_plane_interval = ttk.Entry(self.frm_parameters, width=9)
        self.cbox_scan_plane = ttk.Combobox(self.frm_parameters, values=['xy', 'yz', 'zx'], state='readonly', width=9)
        # Place widgets within grid
        self.btn_load_part_alignment.grid(column=0, row=0, sticky='new', padx=5, pady=5)
        self.btn_scan_point.grid(column=0, row=1, sticky='new', padx=5, pady=(0,5))
        self.btn_scan_line.grid(column=0, row=2, sticky='new', padx=5, pady=(0,5))
        self.btn_run_pause.grid(column=0, row=3, sticky='new', padx=5, pady=(0,5))
        self.btn_stop_mapping.grid(column=0, row=4, sticky='new', padx=5, pady=(0,5))
        self.lbl_start_point.grid(column=0, row=0, columnspan=6)
        self.lbl_sp_x.grid(column=0, row=1, sticky='e')
        self.lbl_sp_y.grid(column=2, row=1, sticky='e')
        self.lbl_sp_z.grid(column=4, row=1, sticky='e')
        self.ent_start_pt_x.grid(column=1, row=1, padx=(5,10), sticky='w')
        self.ent_start_pt_y.grid(column=3, row=1, padx=(5,10),sticky='w')
        self.ent_start_pt_z.grid(column=5, row=1, padx=(5,10), sticky='w')
        self.lbl_scan_volume.grid(column=0, row=0, columnspan=6)
        self.lbl_sv_x.grid(column=0, row=1, sticky='e')
        self.lbl_sv_y.grid(column=2, row=1, sticky='e')
        self.lbl_sv_z.grid(column=4, row=1, sticky='e')
        self.ent_scan_volume_x.grid(column=1, row=1, padx=(5,10), sticky='w')
        self.ent_scan_volume_y.grid(column=3, row=1, padx=(5,10), sticky='w')
        self.ent_scan_volume_z.grid(column=5, row=1, padx=(5,10), sticky='w')
        self.lbl_sampling_interval.grid(column=0, row=0, columnspan=2, sticky='w')
        self.lbl_scanning_plane_interval.grid(column=2, row=0, columnspan=2, sticky='w')
        self.lbl_scanning_plane.grid(column=4, row=0, columnspan=2, sticky='w')
        self.ent_sampling_interval.grid(column=0, row=1, padx=5)
        self.ent_sampling_interval.tooltip = ToolTip(self.ent_sampling_interval, 'Default value 0.5', delay=600)
        self.ent_scan_plane_interval.grid(column=2, row=1, padx=5)
        self.cbox_scan_plane.grid(column=4, row=1, columnspan=2, sticky='w')
        self.ent_sampling_interval.insert(tk.END, '0.5')
        self.ent_scan_plane_interval.insert(tk.END, '0.0')
        self.cbox_scan_plane.set('xy')

    # def connect_cmm(self):
    #     try:
    #         self.zeiss = CMM(ip='192.4.1.200', port=4712)
    #         self.lbl_conn_status['text'] = 'Connection Established'
    #     except ConnectionRefusedError:
    #         self.lbl_conn_status['text'] = 'Connection Refused'
    #     except TimeoutError:
    #         self.lbl_conn_status['text'] = 'Connection Timed Out'

    # def disconnect_cmm(self):
    #     try:
    #         self.zeiss.close()
    #         self.lbl_conn_status['text'] = 'Disconnected'
    #     except AttributeError:
    #         self.lbl_conn_status['text'] = 'Already Disconnected'


class PlotField(tk.Frame):
    '''
    tk frame for plotting magnetic field data
    '''
    def __init__(self, parent):
        self.plotfield_parent = parent
        super().__init__(parent)
        self.create_plot()

    def create_plot(self):
        data = np.genfromtxt('fieldmap_reduced.txt')
        cmm_xyz = data[:, :3]
        Bxyz = data[:, 3:]
        Bxyz_norm = np.linalg.norm(Bxyz, axis=1)
        self.fig = Figure(figsize=(8,4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plotfield_parent)
        self.canvas.draw()
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.fig.subplots_adjust(left=0.05, right=0.95, bottom=0.05, top=0.95)
        self.ax.set_title(' Field Strength Map')
        self.ax.set_xlabel('x axis [mm]')
        self.ax.set_ylabel('y axis [mm]')
        self.ax.set_zlabel('Field Strength [mT]')
        plot3d = self.ax.scatter(cmm_xyz[:, 0], cmm_xyz[:, 1], Bxyz_norm, c=Bxyz_norm, cmap='rainbow', marker='.')
        self.fig.colorbar(plot3d, ax=self.ax, label='mT', pad=0.1)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plotfield_parent)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP,
                                         fill=tk.BOTH, expand=1)

class PlotTemperature(tk.Frame):
    '''
    tk frame for plotting temperature sensor data
    '''
    def __init__(self, parent):
        self.plot_temp_parent = parent
        super().__init__(parent)
        self.create_widgets()
    
    def create_widgets(self):
        '''
        change to set graph labels at start of measurement
        '''
        self.fig = Figure(figsize=(8,4))
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title('Magnet Temperature')
        self.ax.set_xlabel('Time [min]')
        self.ax.set_ylabel(r'Temperature [$^\circ$C]')
        self.ax.grid()
        self.graph = FigureCanvasTkAgg(self.fig, self.plot_temp_parent)
        self.graph.draw()
        self.ax.plot([1,2,3,4,5,6,7,8], [19.8, 19.9, 20, 20, 20.5, 20.7, 20.8, 21], label='channel 0')
        self.ax.legend()
        self.toolbar = NavigationToolbar2Tk(self.graph, self.plot_temp_parent)
        self.toolbar.update()
        self.graph.get_tk_widget().pack()

class FieldFrame(tk.Frame):
    '''
    Parent tk frame for magnetic field plot.
    This frame is used for gui placement only.
    '''
    def __init__(self, parent):
        self.field_frame_parent = parent
        super().__init__(parent)
        self.field_plot = PlotField(self)

class TemperatureFrame(tk.Frame):
    '''
    Parent tk frame for temperature plot.
    This frame is used for gui placement only.
    '''
    def __init__(self, parent):
        self.temp_frame_parent = parent
        super().__init__(parent)
        self.temp_plot = PlotTemperature(self)

class ProbeQualification(ttk.LabelFrame):
    '''
    tk frame for qualifying the hall probe sensor.
    Qualification process consists of:
        * zero gauss offset
        * xyz offset using fsv tool
        * sensor orthogonalization using cube tool
    '''
    def __init__(self, parent):
        self.calib_tools_parent = parent
        super().__init__(parent, text='Hall Sensor Qualification', labelanchor='nw')
        self.fsv_filepath = tk.StringVar()
        self.cube_filepath = tk.StringVar()
        self.zero_gauss_filepath = tk.StringVar()
        self.probe_calib_filepath = tk.StringVar()
        self.create_widgets()

    def create_widgets(self):
        self.btn_run_zg = ttk.Button(self, text='Run Zero Gauss Offset',
                                       command=self.run_zero_gauss)
        self.btn_run_fsv = ttk.Button(self, text='Run FSV Qualification',
                                      command=self.run_fsv, state='disabled')
        self.btn_run_cube = ttk.Button(self, text='Run Cube Qualification',
                                       command=self.run_cube, state='disabled')
        self.btn_verify_qualification = ttk.Button(self, text='Verify Qualification',
                                                   command=self.verify_qualification)
        self.lbl_instructions = ttk.Label(self, text='Qualification Instructions')
        self.txt_instructions = tk.Text(self, wrap=tk.WORD, height=11, width=40, state='normal')
        with open('qualification_instructions.txt', 'r') as file:
            instructions = file.read()
        self.txt_instructions.insert(tk.END, instructions)
        # Place widgets within grid
        self.btn_run_zg.grid(column=0, row=1, sticky='new', padx=5, pady=(5,0))
        self.btn_run_fsv.grid(column=0, row=2, sticky='new', padx=5, pady=(5,0))
        self.btn_run_cube.grid(column=0, row=3, sticky='new', padx=5, pady=(5,0))
        self.btn_verify_qualification.grid(column=0, row=4, sticky='new', padx=5, pady=(5,0))
        self.lbl_instructions.grid(column=1, row=0, sticky='w', padx=5, pady=(5,0))
        self.txt_instructions.grid(column=1, row=1, rowspan=4, sticky='nw', padx=5, pady=(0,5))
        self.txt_instructions.configure(state='disabled')

    def load_filepath(self, filepath, enable=None):
        filepath = tk.filedialog.askopenfilename(filetypes=[('Text Files', '*.txt'), ('All Files', '*.*')])
        if enable != None:
            enable.configure(state='enabled')
    
    def run_zero_gauss(self):
        zg = zgWindow(self)
        self.btn_run_fsv.configure(state='enabled')
    
    def run_fsv(self):
        fsv = fsvWindow(self)
        self.btn_run_cube.configure(state='enabled')
    
    def run_cube(self):
        cube = CubeWindow(self)
    
    def verify_qualification(self):
        zg = isfile('zg_calib_coeffs.npy')
        fsv = isfile('fsv_offset.txt')
        cube = isfile('sensitivity.npy')
        instructions = ['Need Zero Gauss Offset',
                        'Need FSV Qualification',
                        'Need Cube Qualification']
        todo = ''
        for i, state in enumerate((zg, fsv, cube)):
            if state == False:
                todo += instructions[i]+'\n'
        if len(todo) > 0:
            showinfo('Qualifications Needed', todo)
        else:
            showinfo('Qualifications Needed', 'All qualifications are complete.')


class ProgramControls(ttk.LabelFrame):
    '''
    Parent tk frame for main program controls such as:
    loading magnet alignment, start/stop measurement,
    saving a measurement and loading a previously saved measurement
    '''
    def __init__(self, parent, title='Program Controls'):
        self.program_controls_parent = parent
        super().__init__(parent, text=title, labelanchor='nw')
        self.create_widgets()

    def create_widgets(self):
        self.btn_load_alignment = ttk.Button(self, text='Load Alignment', command=self.load_alignment)
        self.btn_start_meas = ttk.Button(self, text='Start Measurement', command=self.start_measurement)
        self.btn_stop_meas = ttk.Button(self, text='Stop Measurement', command=self.stop_measurement, state='disabled')
        self.btn_load_meas = ttk.Button(self, text='Load Measurement', command=self.load_measurement)
        self.btn_save_meas = ttk.Button(self, text='Save Measurement', command=self.save_measurement)
        self.lbl_controls_status = tk.Label(self, text='*Program Controls Status*')
        self.lbl_controls_status.config(relief='sunken')
        # Place widgets within grid
        self.btn_load_alignment.grid(column=0, row=0, padx=5, pady=5, sticky='new')
        self.btn_start_meas.grid(column=1, row=0, padx=5, pady=5, sticky='new')
        self.btn_stop_meas.grid(column=2, row=0, padx=5, pady=5, sticky='new')
        self.btn_load_meas.grid(column=0, row=1, padx=5, pady=5, sticky='new')
        self.btn_save_meas.grid(column=1, row=1, padx=5, pady=5, sticky='new')
        self.lbl_controls_status.grid(column=0, row=2, columnspan=3, padx=5, pady=5, sticky='sew')
    
    def load_alignment(self):
        self.alignment_file = tk.filedialog.askopenfilename(filetypes=[('Text Files', '*.txt'), ('All Files', '*.*')])
        if self.alignment_file != '':
            self.lbl_controls_status.configure(text=f'Loaded alignment file\n{self.alignment_file}')

    def start_measurement(self):
        self.btn_start_meas.configure(state='disabled')
        self.btn_load_alignment.configure(state='disabled')
        self.btn_load_meas.configure(state='disabled')
        self.btn_save_meas.configure(state='disabled')
        self.btn_stop_meas.configure(state='enabled')
        StartMeasurement(self)
    
    def stop_measurement(self):
        self.program_controls_parent.zeiss_frame.zeiss.send('D99\r\n'.encode('ascii'))
        self.program_controls_parent.zeiss_frame.disconnect_cmm()
        self.btn_start_meas.configure(state='enabled')
        self.btn_load_alignment.configure(state='enabled')
        self.btn_load_meas.configure(state='enabled')
        self.btn_stop_meas.configure(state='disabled')
        self.lbl_controls_status.configure(text='Measurement stopped')

    def save_measurement(self):
        self.save_file = tk.filedialog.asksaveasfilename(filetypes=[('Text Files', '*.txt'), ('CSV Files', '*.csv')])

    def load_measurement(self):
        pass

class StartMeasurement(tk.Frame):
    '''
    Empty tk frame used for starting a measurement session based on
    set parameters and loaded magnet alignment.
    '''
    def __init__(self, parent):
        self.start_meas_parent = parent
        super().__init__(parent)
        
if __name__ == '__main__':
    app = HallProbeApp(tk.Tk())
    app.master.protocol('WM_DELETE_WINDOW', app.on_closing)
    app.master.mainloop()