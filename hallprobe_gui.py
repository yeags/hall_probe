import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo, showerror
from tkinter.scrolledtext import ScrolledText
from tkinter import filedialog
from tkinter.simpledialog import askstring
from fsv import fsvWindow
from cube import CubeWindow
from zero_gauss import zgWindow
from mapping import MapFrames
import numpy as np
import os
import pickle
from os.path import isfile
from pathlib import Path
import matplotlib
matplotlib.use("TkAgg")
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from plots import PlotWindow

from tooltip import ToolTip

class HallProbeApp(tk.Frame):
    '''
    Master tk frame to place all containers in.
    '''
    def __init__(self, master):
        self.master = master
        self.working_dir = Path(os.getcwd())
        self.measurement_plan = None
        self.images_dir = self.working_dir / 'images'
        super().__init__(master)
        self.master.resizable(0,0)
        self.master.title('Hall Probe CMM Program')
        self.master.iconbitmap('magnet.ico')
        self.master.geometry('1350x900')
        self.create_frames()
    
    def create_frames(self):
        self.controls = ControlsFrame(self)
        self.visuals = VisualsFrame(self)
        self.grid(column=0, row=0, sticky='nsew')
        self.controls.grid(column=0, row=0, padx=5, pady=5, sticky='nsew')
        self.visuals.grid(column=1, row=0, padx=(0,5), pady=(5,0), sticky='nsew')
    
    def update_graph_labels(self):
        self.visuals.temp_plot.temp_frame_parent.temp_plot.update_labels()
    
    def on_closing(self):
        if tk.messagebox.askokcancel('Quit', 'Do you want to quit?'):
            self.controls.map_field_frame.frm_mp.close_mapping()
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
        self.lbl_magname = tk.Label(self, text='Magnet Name')
        self.lbl_serial = tk.Label(self, text='Serial Number')
        self.lbl_current = tk.Label(self, text='Current (A)')
        self.lbl_notes = tk.Label(self, text='Notes')
        self.ent_magname = ttk.Entry(self)
        self.ent_serial = ttk.Entry(self)
        self.ent_current = ttk.Entry(self)
        self.txt_notes = ScrolledText(self, width=60, height=12)
        self.btn_save = ttk.Button(self, text='Save', command=self.save_info)
        # Place widgets within grid
        self.lbl_magname.grid(column=0, row=0, sticky='w', padx=5)
        self.lbl_serial.grid(column=1, row=0, sticky='w', padx=5)
        self.lbl_current.grid(column=2, row=0, sticky='w', padx=5)
        self.lbl_notes.grid(column=0, row=2, sticky='w', padx=5, pady=(5,0))
        self.ent_magname.grid(column=0, row=1, sticky='w', padx=5, pady=(0,5))
        self.ent_serial.grid(column=1, row=1, sticky='w', padx=5, pady=(0,5))
        self.ent_current.grid(column=2, row=1, sticky='w', padx=5, pady=(0,5))
        self.txt_notes.grid(column=0, row=3, columnspan=3, sticky='nw', padx=5, pady=(0,5))
        self.btn_save.grid(column=0, row=4, sticky='w', padx=5, pady=(0,5))
    
    def save_info(self):
        '''
        Save magnet info to a pickle file
        '''
        magname = self.ent_magname.get()
        serial = self.ent_serial.get()
        current = self.ent_current.get()
        notes = self.txt_notes.get('1.0', 'end-1c')
        header = [magname, serial, current, notes]
        if magname and serial and current:
            with open('magnet_info.pkl', 'wb') as f:
                pickle.dump(header, f)
        else:
            showerror('Error', 'Please enter all information. Notes are optional.')

class MapField(ttk.LabelFrame):
    '''
    tk frame for inputting measurement parameters such as
    starting coordinate, scan length, speed, and measurement interval
    '''
    def __init__(self, parent, title='Field Mapping'):
        self.map_field_parent = parent
        super().__init__(parent, text=title, labelanchor='nw')
        self.create_frame()

    def create_frame(self):
        self.frm_mp = MapFrames(self)
        self.frm_mp.grid(column=0, row=0)

class PlotField(tk.Frame):
    '''
    tk frame for plotting magnetic field data
    '''
    def __init__(self, parent):
        self.plotfield_parent = parent
        super().__init__(parent)
        self.create_plot()

    def create_plot(self):
        data = np.genfromtxt('area.txt')
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
        self.ax.set_ylabel('z axis [mm]')
        self.ax.set_zlabel('Field Strength [mT]')
        plot3d = self.ax.scatter(cmm_xyz[:, 0], cmm_xyz[:, 2], Bxyz_norm,
                                 c=Bxyz_norm, cmap='rainbow', marker='.')
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
                                      command=self.run_fsv)
        self.btn_run_cube = ttk.Button(self, text='Run Cube Qualification',
                                       command=self.run_cube)
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

    # def load_filepath(self, filepath, enable=None):
    #     filepath = tk.filedialog.askopenfilename(filetypes=[('Text Files', '*.txt'), ('All Files', '*.*')])
    #     if enable != None:
    #         enable.configure(state='enabled')
    
    def run_zero_gauss(self):
        zg = zgWindow(self)
    
    def run_fsv(self):
        fsv = fsvWindow(self)
    
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
        self.scans_folder = './scans/'
        self.measurement_session = None
        super().__init__(parent, text=title, labelanchor='nw')
        self.create_widgets()

    def create_widgets(self):
        self.btn_plot = ttk.Button(self, text='Plot Data', command=self.plot_window)
        self.lbl_controls_status = tk.Label(self, text='*Program Controls Status*')
        self.lbl_controls_status.config(relief='sunken')
        # Place widgets within grid
        self.btn_plot.grid(column=0, row=0, sticky='new', padx=5, pady=5)
        self.lbl_controls_status.grid(column=0, row=1, columnspan=3, padx=5, pady=5, sticky='sew')
    
    def plot_window(self):
        plot = PlotWindow(self)


if __name__ == '__main__':
    app = HallProbeApp(tk.Tk())
    app.master.protocol('WM_DELETE_WINDOW', app.on_closing)
    app.master.mainloop()