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
        self.master.geometry('1200x800')
        self.create_frames()
        self.pack(side='left', padx=30, fill='both')
    
    def create_frames(self):
        self.zeiss_frame = ZeissControls(self)
        self.zeiss_frame.grid(column=0, row=0, sticky='w')
        self.daq_frame = DaqControls(self)
        self.daq_frame.grid(column=0, row=1, sticky='w')
        self.plot_data_frame = PlotData(self)
        self.plot_data_frame.grid(column=1, row=0, sticky='e')

class ZeissControls(ttk.LabelFrame):
    def __init__(self, parent, title='Zeiss CMM Controls', labelanchor='n'):
        super().__init__(parent, text=title, labelanchor='n')
        self.create_widgets()
        self.grid(pady=30)
    
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
        self.therm_channels = []
        self.therm_chan_var = []
        self.volt_channels = []
        self.volt_chan_var = []
        self.therm_types = Constants.therm_types()
        self.create_widgets()

    def create_widgets(self):
        self.lbl_therm_channel = tk.Label(self, text='Thermocouple Channels')
        self.lbl_therm_channel.grid(column=0, row=0)
        
        for i in range(8): # Create Thermocouple channel check buttons
            var = tk.IntVar(value=0)
            chk_therm_channel = ttk.Checkbutton(self, text=f'Channel {i}', variable=var)
            chk_therm_channel.grid(column=0, row=1+i, sticky='w')
            self.therm_channels.append(chk_therm_channel)
            self.therm_chan_var.append(var)
        
        self.lbl_volt_channel = tk.Label(self, text='Voltage Channels')
        self.lbl_volt_channel.grid(column=1, row=0, padx=10)

        for j in range(4): # Create Voltage channel check buttons
            var = tk.IntVar(value=0)
            chk_volt_channel = ttk.Checkbutton(self, text=f'Channel {j}', variable=var)
            chk_volt_channel.grid(column=1, row=1+j, sticky='w', padx=10)
            self.volt_channels.append(chk_volt_channel)
            self.volt_chan_var.append(var)
        
class PlotData(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()
    
    def create_widgets(self):
        # self.graphTitle = ttk.Label(self, text='')
        self.fig = Figure(figsize=(7,5))
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title('Vector Field Map')
        self.graph = FigureCanvasTkAgg(self.fig, self)
        self.graph.draw()
        self.graph.get_tk_widget().pack()


if __name__ == '__main__':
    app = HallProbeApp(tk.Tk())
    app.mainloop()