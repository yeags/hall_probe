import tkinter as tk
import numpy as np

import matplotlib
from matplotlib.figure import Figure
matplotlib.use('TkAgg')
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

class PlotField3D(tk.Frame):
    def __init__(self, parent):
        self.sp_index = {
            'xy': [0, 1],
            'yz': [1, 2],
            'zx': [2, 0]
        }
        self.axes_labels = [
            'x axis [mm]',
            'y axis [mm]',
            'z axis [mm]'
        ]
        self.plot3d_parent = parent
        super().__init__(parent)

    def create_plot(self, data, scan_plane):
        Bxyz_norm = np.linalg.norm(data[:, 3:], axis=1)
        self.fig = Figure(figsize=(8,4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot3d_parent)
        self.canvas.draw()
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.fig.subplots_adjust(left=0.05, right=0.95, bottom=0.05, top=0.92)
        self.ax.set_title('3D Field Strength Plot')
        self.ax.set_xlabel(self.axes_labels[self.sp_index[scan_plane][0]])
        self.ax.set_ylabel(self.axes_labels[self.sp_index[scan_plane][1]])
        self.ax.set_zlabel('Field Strength [mT]')
        plot3d = self.ax.scatter(data[:, self.sp_index[scan_plane][0]],
                                 data[:, self.sp_index[scan_plane][1]], Bxyz_norm,
                                 c=Bxyz_norm, cmap='rainbow', marker='.')
        self.fig.colorbar(plot3d, ax=self.ax, label='Field Strength [mT]', pad=0.1)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot3d_parent)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

class PlotField2D(tk.Frame):
    def __init__(self, parent):
        self.sp_index = {
            'xy': [0, 1],
            'yz': [1, 2],
            'zx': [2, 0]
        }
        self.axes_labels = [
            'x axis [mm]',
            'y axis [mm]',
            'z axis [mm]'
        ]
        self.plot2d_parent = parent
        super().__init__(parent)

    def create_plot(self, data, scan_plane):
        Bxyz_norm = np.linalg.norm(data[:, 3:], axis=1)
        self.fig = Figure(figsize=(8,4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot2d_parent)
        self.canvas.draw()
        self.ax = self.fig.add_subplot(111)
        # self.fig.subplots_adjust(left=0.05, right=0.95, bottom=0.05, top=0.95)
        self.ax.set_title('2D Field Strength Plot')
        self.ax.set_xlabel(self.axes_labels[self.sp_index[scan_plane][0]])
        self.ax.set_ylabel(self.axes_labels[self.sp_index[scan_plane][1]])
        self.ax.grid()
        plot2d = self.ax.scatter(
            data[:, self.sp_index[scan_plane][0]],
            data[:, self.sp_index[scan_plane][1]],
            c=Bxyz_norm, cmap='rainbow', marker='.'
        )
        self.fig.colorbar(plot2d, ax=self.ax, label='Field Strength [mT]', pad=0.1)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot2d_parent)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

class PlotTemperature(tk.Frame):
    def __init__(self, parent):
        self.plot_temp_parent = parent
        super().__init__(parent)

    def create_plot(self, data):
        pass

class PlotSignal(tk.Frame):
    def __init__(self, parent):
        self.plot_signal_parent = parent
        super().__init__(parent)
    
    def create_plot(self, data):
        pass

class PlotPointCloud(tk.Frame):
    def __init__(self, parent):
        self.plot_pointcloud_parent = parent
        super().__init__(parent)
    
    def create_plot(self, data):
        Bxyz_norm = np.linalg.norm(data[:, 3:], axis=1)
        self.fig = Figure(figsize=(8,4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_pointcloud_parent)
        self.canvas.draw()
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.fig.subplots_adjust(left=0.05, right=0.95, bottom=0.05, top=0.92)
        self.ax.set_title('3D Field Strength Point Cloud')
        self.ax.set_xlabel('x axis [mm]')
        self.ax.set_ylabel('y axis [mm]')
        self.ax.set_zlabel('z axis [mm]')
        plot_pc = self.ax.scatter(
            data[:, 0], data[:, 1], data[:, 2],
            c=Bxyz_norm, cmap='rainbow', marker='.')
        self.fig.colorbar(plot_pc, ax=self.ax, label='Field Strength [mT]', pad=0.1)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_pointcloud_parent)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

if __name__ == '__main__':
    data = np.genfromtxt('fieldmap_reduced.txt')
    sp = ['xy', 'xy', '']
    root = tk.Tk()
    f = [tk.Frame(root), tk.Frame(root), tk.Frame(root)]
    p = [PlotField2D(f[0]), PlotField3D(f[1]), PlotPointCloud(f[2])]
    for i, fig in enumerate(p):
        if sp[i] != '':
            fig.create_plot(data, sp[i])
        else:
            fig.create_plot(data)
    f[0].grid(column=0, row=0)
    f[1].grid(column=1, row=0)
    f[2].grid(column=0, row=1)
    # plot = PlotField3D(root)
    # plot = PlotField2D(root)
    # plot = PlotPointCloud(root)
    # plot.create_plot(data, 'xy')
    # plot.create_plot(data)
    root.mainloop()