import tkinter as tk
from tkinter import ttk
from zeisscmm import CMM
from fsv import fsvWindow
from cube import CubeWindow
from zero_gauss import zgWindow
import numpy as np
from datetime import datetime
import threading
import calibration

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
        self.master.title('Hall Probe CMM Program')
        self.master.iconbitmap('magnet.ico')
        self.master.geometry('1350x900')
        self.create_frames()
    
    def create_frames(self):
        self.controls = ControlsFrame(self)
        self.visuals = VisualsFrame(self)
        self.pack()
        self.controls.grid(column=0, row=0, padx=5, pady=5)
        self.visuals.grid(column=1, row=0, padx=5, pady=5)
    
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
        self.zeiss_frame = ZeissControls(self)
        self.calibration_frame = ProbeQualification(self)
        self.program_frame = ProgramControls(self)

        self.magnet_info_frame.grid(column=0, row=0)
        self.zeiss_frame.grid(column=0, row=1)
        self.calibration_frame.grid(column=0, row=2)
        self.program_frame.grid(column=0, row=4)

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
        super().__init__(parent, text=title, labelanchor='n')
        self.create_widgets()

    def create_widgets(self):
        self.lbl_partnum = tk.Label(self, text='Part Number')
        self.ent_partnum = ttk.Entry(self)
        self.lbl_serial = tk.Label(self, text='Serial Number')
        self.ent_serial = ttk.Entry(self)

        self.lbl_partnum.grid(column=0, row=0, sticky='w', padx=5)
        self.ent_partnum.grid(column=0, row=1, sticky='w', padx=5, pady=(0,5))
        self.lbl_serial.grid(column=1, row=0, sticky='w', padx=5)
        self.ent_serial.grid(column=1, row=1, sticky='w', padx=5, pady=(0,5))

class ZeissControls(ttk.LabelFrame):
    '''
    tk frame for inputting CMM parameters such as
    starting coordinate, scan length, speed, and measurement interval
    '''
    def __init__(self, parent, title='Zeiss CMM Controls'):
        self.zeiss_controls_parent = parent
        super().__init__(parent, text=title, labelanchor='n')
        self.grid(pady=20)
        self.create_widgets()
    
    def create_widgets(self):
        self.btn_emerg_stop = ttk.Button(self, text='Emergency Stop', command=self.emergency_stop)
        self.lbl_conn_status = tk.Label(self, text='*Connection Status*')
        self.lbl_conn_status.config(relief='sunken')
        self.lbl_start_pt = tk.Label(self, text='Start Point')
        self.lbl_start_pt_x = tk.Label(self, text='X')
        self.ent_start_pt_x = ttk.Entry(self, width=9)
        self.lbl_start_pt_y = tk.Label(self, text='Y')
        self.ent_start_pt_y = ttk.Entry(self, width=9)
        self.lbl_start_pt_z = tk.Label(self, text='Z')
        self.ent_start_pt_z = ttk.Entry(self, width=9)
        self.lbl_scan_length = tk.Label(self, text='Scan Length')
        self.lbl_scan_length_x = tk.Label(self, text='X')
        self.ent_scan_length_x = ttk.Entry(self, width=9)
        self.lbl_scan_length_y = tk.Label(self, text='Y')
        self.ent_scan_length_y = ttk.Entry(self, width=9)
        self.lbl_scan_length_z = ttk.Label(self, text='Z')
        self.ent_scan_length_z = ttk.Entry(self, width=9)

        self.btn_emerg_stop.grid(column=0, row=0, columnspan=6)
        self.lbl_conn_status.grid(column=0, row=1, columnspan=6, padx=5, pady=5, sticky='ew')
        self.lbl_start_pt.grid(column=0, row=2, columnspan=6)
        self.lbl_start_pt_x.grid(column=0, row=3)
        self.ent_start_pt_x.grid(column=1, row=3)
        self.lbl_start_pt_y.grid(column=2, row=3)
        self.ent_start_pt_y.grid(column=3, row=3)
        self.lbl_start_pt_z.grid(column=4, row=3)
        self.ent_start_pt_z.grid(column=5, row=3)
        self.lbl_scan_length.grid(column=0, row=4, columnspan=6)
        self.lbl_scan_length_x.grid(column=0, row=5)
        self.ent_scan_length_x.grid(column=1, row=5)
        self.lbl_scan_length_y.grid(column=2, row=5)
        self.ent_scan_length_y.grid(column=3, row=5)
        self.lbl_scan_length_z.grid(column=4, row=5)
        self.ent_scan_length_z.grid(column=5, row=5)

    def emergency_stop(self):
        pass
    
    def connect_cmm(self):
        try:
            self.zeiss = CMM(ip='192.4.1.200', port=4712)
            self.lbl_conn_status['text'] = 'Connection Established'
        except ConnectionRefusedError:
            self.lbl_conn_status['text'] = 'Connection Refused'
        except TimeoutError:
            self.lbl_conn_status['text'] = 'Connection Timed Out'

    def disconnect_cmm(self):
        try:
            self.zeiss.close()
            self.lbl_conn_status['text'] = 'Disconnected'
        except AttributeError:
            self.lbl_conn_status['text'] = 'Already Disconnected'


class PlotField(tk.Frame):
    '''
    tk frame for plotting magnetic field data
    '''
    def __init__(self, parent):
        self.plotfield_parent = parent
        super().__init__(parent)
        self.create_plot()

    def create_plot(self):
        x, y, z = np.meshgrid(np.arange(-0.8, 1, 0.2),
                              np.arange(-0.8, 1, 0.2),
                              np.arange(-0.8, 1, 0.8))
        u = np.sin(np.pi * x) * np.cos(np.pi * y) * np.cos(np.pi * z)
        v = -np.cos(np.pi * x) * np.sin(np.pi * y) * np.cos(np.pi * z)
        w = (np.sqrt(2.0 / 3.0) * np.cos(np.pi * x) * np.cos(np.pi * y) * np.sin(np.pi * z))
        self.fig = Figure(figsize=(8,4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plotfield_parent)
        self.canvas.draw()
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
        self.ax.set_title('Vector Field Map')
        self.ax.set_xlabel('x axis [mm]')
        self.ax.set_ylabel('y axis [mm]')
        self.ax.set_zlabel('z axis [mm]')
        self.ax.quiver(x, y, z, u, v, w, length=0.15, normalize=True)
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
        super().__init__(parent, text='Hall Sensor Qualification', labelanchor='n')
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
        self.lbl_instructions = ttk.Label(self, text='Qualification Instructions')
        self.txt_instructions = tk.Text(self, wrap=tk.WORD, height=11, width=40, state='disabled')

        self.btn_run_zg.grid(column=0, row=0, sticky='w', padx=5, pady=(5,0))
        self.btn_run_fsv.grid(column=0, row=1, sticky='w', padx=5, pady=(5,0))
        self.btn_run_cube.grid(column=0, row=2, sticky='w', padx=5, pady=(5,0))
        self.lbl_instructions.grid(column=1, row=0, sticky='w', padx=5, pady=(5,0))
        self.txt_instructions.grid(column=1, row=1, rowspan=2, sticky='nw', padx=5, pady=(0,5))

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
        self.btn_load_zero_gauss.configure(state='enabled')

class ProgramControls(ttk.LabelFrame):
    '''
    Parent tk frame for main program controls such as:
    loading magnet alignment, start/stop measurement,
    saving a measurement and loading a previously saved measurement
    '''
    def __init__(self, parent, title='Program Controls'):
        self.program_controls_parent = parent
        super().__init__(parent, text=title, labelanchor='n')
        self.create_widgets()

    def create_widgets(self):
        self.btn_load_alignment = ttk.Button(self, text='Load Alignment', command=self.load_alignment)
        self.btn_start_meas = ttk.Button(self, text='Start Measurement', command=self.start_measurement)
        self.btn_stop_meas = ttk.Button(self, text='Stop Measurement', command=self.stop_measurement, state='disabled')
        self.btn_load_meas = ttk.Button(self, text='Load Measurement', command=self.load_measurement)
        self.btn_save_meas = ttk.Button(self, text='Save Measurement', command=self.save_measurement)
        self.lbl_controls_status = tk.Label(self, text='*Program Controls Status*')
        self.lbl_controls_status.config(relief='sunken')
        self.btn_load_alignment.grid(column=0, row=0, padx=5, pady=5, sticky='e')
        self.btn_start_meas.grid(column=1, row=0, padx=5, pady=5, sticky='w')
        self.btn_stop_meas.grid(column=2, row=0, padx=5, pady=5, sticky='w')
        self.btn_load_meas.grid(column=0, row=1, padx=5, pady=5, sticky='e')
        self.btn_save_meas.grid(column=1, row=1, padx=5, pady=5, sticky='w')
        self.lbl_controls_status.grid(column=0, row=2, columnspan=3, padx=5, pady=5, sticky='ew')
    
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