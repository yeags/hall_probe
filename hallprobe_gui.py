import tkinter as tk
from tkinter import ttk
from zeisscmm import CMM
from nicdaq import DAQ, Constants

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class HallProbeApp(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.master.title('Hall Probe Integration App')
        self.master.geometry('1200x850')
        self.create_frames()
        self.pack(side='left', padx=30, fill='both')
    
    def create_frames(self):
        self.zeiss_frame = ZeissControls(self)
        self.zeiss_frame.grid(column=0, row=0, rowspan=2, sticky='n')
        self.daq_frame = DaqControls(self)
        self.daq_frame.grid(column=0, row=1, rowspan=2, sticky='n')
        self.plot_data_frame = PlotData(self)
        self.plot_data_frame.grid(column=1, row=0, sticky='e')
        self.plot_temperature_frame = PlotTemperature(self)
        self.plot_temperature_frame.grid(column=1, row=1)

class ZeissControls(ttk.LabelFrame):
    def __init__(self, parent, title='Zeiss CMM Controls', labelanchor='n'):
        super().__init__(parent, text=title, labelanchor='n')
        self.grid(pady=30)
        self.create_widgets() 
    
    def create_widgets(self):
        self.lbl_ip = tk.Label(self, text='IP Address')
        self.lbl_ip.grid(column=0, row=0, sticky='e')
        self.ent_ip = tk.Entry(self)
        self.ent_ip.insert(0, '192.4.1.200')
        self.ent_ip.grid(column=1, row=0)
        self.lbl_port = tk.Label(self, text='Port')
        self.lbl_port.grid(column=0, row=1, sticky='e')
        self.ent_port = tk.Entry(self)
        self.ent_port.insert(0, '4712')
        self.ent_port.grid(column=1, row=1)
        self.btn_connect = tk.Button(self, text='Connect', command=self.connect_cmm)
        self.btn_connect.grid(column=0, row=2)
        self.btn_disconnect = tk.Button(self, text='Disconnect', command=self.disconnect_cmm)
        self.btn_disconnect.grid(column=1, row=2)
        self.lbl_conn_status = tk.Label(self, text='*Connection Status*')
        self.lbl_conn_status.grid(column=0, row=3, columnspan=2)

    def connect_cmm(self):
        try:
            self.zeiss = CMM(ip=self.ent_ip.get(), port=int(self.ent_port.get()))
            self.btn_connect['state'] = 'disabled'
            self.lbl_conn_status['text'] = 'Connection Established'
        except ConnectionRefusedError:
            self.lbl_conn_status['text'] = 'Connection Refused'
        except TimeoutError:
            self.lbl_conn_status['text'] = 'Connection Timed Out'

    def disconnect_cmm(self):
        try:
            self.zeiss.close()
            self.btn_connect['state'] = 'normal'
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
        self.therm_channels = []
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
            self.therm_channels.append(chk_therm_channel)
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
        self.volt_channels = []
        self.volt_chan_var = []
        self.create_frame()

    def create_frame(self):
        for j in range(4): # Create Voltage channel check buttons
            var = tk.IntVar(value=0)
            chk_volt_channel = ttk.Checkbutton(self, text=f'Channel {j}', variable=var)
            chk_volt_channel.grid(column=1, row=1+j, sticky='w', padx=10)
            self.volt_channels.append(chk_volt_channel)
            self.volt_chan_var.append(var)
        for i in range(3):
            self.volt_chan_var[i].set(1)
        

class PlotData(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()
    
    def create_widgets(self):
        # self.graphTitle = ttk.Label(self, text='')
        self.fig = Figure(figsize=(8,4))
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title('Vector Field Map')
        self.graph = FigureCanvasTkAgg(self.fig, self)
        self.graph.draw()
        self.graph.get_tk_widget().grid(padx=30, pady=10)
        # self.graph.get_tk_widget().pack()

class PlotTemperature(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()
    
    def create_widgets(self):
        # self.graphTitle = ttk.Label(self, text='')
        self.fig = Figure(figsize=(8,4))
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title('Magnet Temperature')
        self.graph = FigureCanvasTkAgg(self.fig, self)
        self.graph.draw()
        self.graph.get_tk_widget().grid(padx=30, pady=10)
        # self.graph.get_tk_widget().pack()

if __name__ == '__main__':
    app = HallProbeApp(tk.Tk())
    app.mainloop()