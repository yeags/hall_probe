import tkinter as tk
from tkinter import ttk
from zeisscmm import CMM
from nicdaq import DAQ, Constants
import numpy as np

import matplotlib
matplotlib.use("TkAgg")
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

class HallProbeApp(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.master.title('Hall Probe Integration App')
        self.master.iconbitmap(r'G:\My Drive\Python\hall_probe\magnet.ico')
        self.master.geometry('1200x900')
        self.create_frames()
    
    def create_frames(self):
        self.controls = ControlsFrame(self)
        self.visuals = VisualsFrame(self)
        self.pack()
        self.controls.grid(column=0, row=0)
        self.visuals.grid(column=1, row=0)

class ControlsFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_frames()
    
    def create_frames(self):
        self.zeiss_frame = ZeissControls(self)
        self.calibration_frame = CalibrationTools(self)
        self.daq_frame = DaqControls(self)
        self.zeiss_frame.grid(column=0, row=0)
        self.calibration_frame.grid(column=0, row=1)
        self.daq_frame.grid(column=0, row=2)


class VisualsFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_frames()

    def create_frames(self):
        self.field_plot = FieldFrame(self)
        self.temp_plot = TemperatureFrame(self)
        self.field_plot.grid(column=0, row=0)
        self.temp_plot.grid(column=0, row=1)

class ZeissControls(ttk.LabelFrame):
    def __init__(self, parent, title='Zeiss CMM Controls'):
        super().__init__(parent, text=title, labelanchor='n')
        # self.grid(pady=30)
        self.create_widgets()
    
    def create_widgets(self):
        self.btn_emerg_stop = ttk.Button(self, text='Emergency Stop', command=self.emergency_stop)
        self.lbl_conn_status = tk.Label(self, text='*Connection Status*')
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
        self.btn_emerg_stop.grid(column=0, row=0, columnspan=6)
        self.lbl_conn_status.grid(column=0, row=1, columnspan=6)
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
    


class DaqControls(ttk.LabelFrame):
    def __init__(self, parent, title='DAQ Controls'):
        super().__init__(parent, text=title, labelanchor='n')
        self.create_widgets()

    def create_widgets(self):
        self.therm_frame = ThermocoupleControls(self)
        self.therm_frame.grid(column=0, row=0, padx=10, pady=10, sticky='n')
        self.volt_frame = VoltageControls(self)
        self.volt_frame.grid(column=1, row=0, padx=10, pady=10, sticky='n')

class ThermocoupleControls(ttk.LabelFrame):
    def __init__(self, parent, title='Thermocouple Controls'):
        super().__init__(parent, text=title, labelanchor='n')
        # self.therm_channels = []
        self.therm_chan_var = []
        self.radio_value_temp_units = tk.StringVar()
        self.therm_types = Constants.therm_types()
        self.temp_units = Constants.temp_units()
        self.create_frame()

    def create_frame(self):
        for i in range(8): # Create Thermocouple channel check buttons
            var = tk.IntVar(value=0)
            chk_therm_channel = ttk.Checkbutton(self, text=f'Channel {i}', variable=var)
            chk_therm_channel.grid(column=0, row=1+i, sticky='w')
            # self.therm_channels.append(chk_therm_channel)
            self.therm_chan_var.append(var)
        self.therm_chan_var[0].set(1)
        self.therm_chan_var[1].set(1)

        self.therm_separator = ttk.Separator(self, orient=tk.HORIZONTAL)
        self.therm_separator.grid(column=0, row=9, sticky='ew')
        self.lbl_therm_type = tk.Label(self, text='Thermocouple Type')
        self.lbl_therm_type.grid(column=0, row=10)
        self.cbox_therm_type = ttk.Combobox(self, values=[i for i in self.therm_types.keys()])
        self.cbox_therm_type['state'] = 'readonly'
        self.cbox_therm_type.grid(column=0, row=11)
        self.cbox_therm_type.current(3)
        self.lbl_temp_units = tk.Label(self, text='Units')
        self.lbl_temp_units.grid(column=0, row=12)
        self.radio_frame = tk.Frame(self)
        self.radio_frame.grid(column=0, row=13, columnspan=3)
        self.radio_btn_c = ttk.Radiobutton(self.radio_frame, text='C', variable=self.radio_value_temp_units, value='C')
        self.radio_btn_f = ttk.Radiobutton(self.radio_frame, text='F', variable=self.radio_value_temp_units, value='F')
        self.radio_btn_k = ttk.Radiobutton(self.radio_frame, text='K', variable=self.radio_value_temp_units, value='K')
        self.radio_value_temp_units.set('C')
        self.radio_btn_c.grid(column=0, row=0)
        self.radio_btn_f.grid(column=1, row=0, padx=10)
        self.radio_btn_k.grid(column=2, row=0)

class VoltageControls(ttk.LabelFrame):
    def __init__(self, parent, title='Voltage Controls'):
        super().__init__(parent, text=title, labelanchor='n')
        # self.volt_channels = []
        self.volt_chan_var = []
        self.create_frame()

    def create_frame(self):
        for j in range(4): # Create Voltage channel check buttons
            var = tk.IntVar(value=0)
            chk_volt_channel = ttk.Checkbutton(self, text=f'Channel {j}', variable=var)
            chk_volt_channel.grid(column=0, row=1+j, columnspan=2, sticky='w', padx=10)
            # self.volt_channels.append(chk_volt_channel)
            self.volt_chan_var.append(var)
        for i in range(3):
            self.volt_chan_var[i].set(1)
        self.lbl_volt_min = tk.Label(self, text='V Min')
        self.lbl_volt_max = tk.Label(self, text='V Max')
        self.ent_volt_min = ttk.Entry(self, width=5)
        self.ent_volt_max = ttk.Entry(self, width=5)
        self.ent_volt_min.insert(0, '-5.0')
        self.ent_volt_max.insert(0, '5.0')
        self.lbl_volt_min.grid(column=0, row = 5)
        self.lbl_volt_max.grid(column=1, row = 5)
        self.ent_volt_min.grid(column=0, row=6)
        self.ent_volt_max.grid(column=1, row=6)
        self.lbl_volt_units = tk.Label(self, text='Units')
        self.lbl_volt_units.grid(column=0, row=7, columnspan=2)
        self.cbox_volt_units = ttk.Combobox(self, values=['V', 'mT'])
        self.cbox_volt_units['state'] = 'readonly'
        self.cbox_volt_units.current(0)
        self.cbox_volt_units.grid(column=0, row=8, columnspan=2)
        

class PlotField(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.create_plot()

    def create_plot(self):
        t = np.arange(0, 3, 0.01)
        self.fig = Figure(figsize=(8,4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.parent)
        self.canvas.draw()
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_title('Vector Field Map')
        self.ax.set_xlabel('x axis [mm]')
        self.ax.set_ylabel('y axis [mm]')
        self.ax.set_zlabel('z axis [mm]')
        self.ax.plot(t, 2*np.sin(2*np.pi*t))
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.parent)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP,
                                         fill=tk.BOTH, expand=1)

class PlotTemperature(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.create_widgets()
    
    def create_widgets(self):
        self.fig = Figure(figsize=(8,4))
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title('Magnet Temperature')
        self.ax.set_xlabel('Time [min]')
        self.ax.set_ylabel('Temperature [C]')
        self.graph = FigureCanvasTkAgg(self.fig, self.parent)
        self.graph.draw()
        self.toolbar = NavigationToolbar2Tk(self.graph, self.parent)
        self.toolbar.update()
        self.graph.get_tk_widget().pack()

class FieldFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.field_plot = PlotField(self)

class TemperatureFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.temp_plot = PlotTemperature(self)

class CalibrationTools(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, text='Calibration Tools', labelanchor='n')
        self.create_widgets()

    def create_widgets(self):
        self.lbl_placeholder = tk.Label(self, text='Placeholder Label')
        self.lbl_placeholder.grid(column=0, row=0)

if __name__ == '__main__':
    app = HallProbeApp(tk.Tk())
    app.mainloop()