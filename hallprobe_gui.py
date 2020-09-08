import tkinter as tk
from tkinter import ttk

class HallProbeApp(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.master.title('Hall Probe Integration App')
        self.master.geometry('1200x800')
        self.create_frames()
        self.pack()
    
    def create_frames(self):
        self.zeiss_frame = ZeissControls(self)
        self.zeiss_frame.grid(column=0, row=0, sticky='w')
        self.hallprobe_frame = HallProbe(self)
        self.hallprobe_frame.grid(column=0, row=1, sticky='w')

class ZeissControls(tk.LabelFrame):
    def __init__(self, parent, title='Zeiss CMM Controls', labelanchor='n'):
        super().__init__(parent, text=title, labelanchor='n')
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
        self.btn_connect = tk.Button(self, text='Connect')
        self.btn_connect.grid(column=0, row=2)
        self.btn_disconnect = tk.Button(self, text='Disconnect')
        self.btn_disconnect.grid(column=1, row=2)
        self.lbl_conn_status = tk.Label(self, text='*Connection Status*')
        self.lbl_conn_status.grid(column=0, row=3, columnspan=2)

class HallProbe(tk.LabelFrame):
    def __init__(self, parent, title='Hall Probe Controls'):
        super().__init__(parent, text=title, labelanchor='n')
        self.create_widgets()

    def create_widgets(self):
        self.lbl_channel = tk.Label(self, text='Channel')
        self.lbl_channel.grid(column=0, row=0)


if __name__ == '__main__':
    app = HallProbeApp(tk.Tk())
    app.mainloop()