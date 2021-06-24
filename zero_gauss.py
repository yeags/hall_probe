import numpy as np
from nicdaq import HallDAQ
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class ZeroGauss:
    def __init__(self):
        self.daq = HallDAQ(1, 20000)
    
    def measure_offset(self):
        self.daq.power_on()
        self.daq.start_hallsensor_task()
        data = self.daq.read_hallsensor()[6250:13750]
        self.daq.stop_hallsensor_task()
        self.daq.power_off()
        self.daq.close_tasks()
        self.zg_offset = np.mean(data, axis=0)
    
    def save_offset(self, filename):
        with open(filename, 'w') as file:
            file.write(f'{self.zg_offset[0]} {self.zg_offset[1]} {self.zg_offset[2]}\n')

class zgWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.frm_zg_window = tk.Frame(self)
        self.frm_zg_window.pack()
        self.img = ImageTk.PhotoImage(Image.open('images/zg_chamber1.jpg'))
        self.geometry('1200x800')
        self.title('Zero Gauss Offset')
        self.create_widgets()
    
    def create_widgets(self):
        self.btn_zg_run = ttk.Button(self.frm_zg_window, text='Record Offset', command=self.run_zg)
        self.btn_close = ttk.Button(self.frm_zg_window, text='Close', command=self.destroy)
        self.lbl_desc = ttk.Label(self.frm_zg_window, text='Move probe into zero gauss chamber as shown.')
        self.lbl_img = ttk.Label(self.frm_zg_window, image=self.img)
        self.btn_zg_run.grid(column=0, row=0, padx=5, pady=5, sticky='nw')
        self.btn_close.grid(column=0, row=1, padx=5, pady=5, sticky='nw')
        self.lbl_desc.grid(column=1, row=0, padx=5, pady=5, sticky='w')
        self.lbl_img.grid(column=1, row=1, padx=5, pady=5)
    
    def run_zg(self):
        zg = ZeroGauss()
        zg.measure_offset()
        zg.save_offset('zg_offset.txt')



if __name__ == '__main__':
    test = ZeroGauss()
    test.measure_offset()
    print(test.zg_offset)
    test.save_offset('zg_offset.txt')