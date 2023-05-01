import numpy as np
from scipy.integrate import quad, cumulative_trapezoid
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import tkinter as tk
from tkinter import ttk

def integrate_line_from_area(data: np.ndarray, integration_axis: str, B_axis: str, scan_spacing: float):
    '''
    data: numpy array (x, y, z, Bx, By, Bz)
    integration_axis: str 'x', 'y', 'z'
    B_axis: str 'Bx', 'By', 'Bz'
    '''
    integration_dict = {'x': 0, 'y': 1, 'z': 2, 'Bx': 3, 'By': 4, 'Bz': 5}
    integral_array = np.zeros((data.shape[0]+1,))
    for i in len(range(1, integral_array.shape[0])):
        integral_array[i] = (data[i, integration_dict[integration_axis]] - data[i-1, integration_dict[integration_axis]]) * (data[i, integration_dict[B_axis]] + data[i-1, integration_dict[B_axis]]) / 2
    integral = np.sum(integral_array)
    return integral

class PlotWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent, takefocus=True)
        self.title = 'Plotting Parameters'
        self.frm_plotwindow = ttk.Frame(self)
        self.frm_plotwindow.pack()
        self.create_widgets()
    
    def create_widgets(self):
        self.lbl_scan_plane = ttk.Label(self.frm_plotwindow, text='Scan Plane')
        self.lbl_plot_axis = ttk.Label(self.frm_plotwindow, text='Plot Axis')
        self.lbl_B_axis = ttk.Label(self.frm_plotwindow, text='B Axis')
        self.lbl_scan_direction = ttk.Label(self.frm_plotwindow, text='Scan Direction')
        self.lbl_z_location = ttk.Label(self.frm_plotwindow, text='z Location')
        self.lbl_scan_spacing = ttk.Label(self.frm_plotwindow, text='Scan Spacing')
        
        self.cbox_scan_plane = ttk.Combobox(self.frm_plotwindow, values=['xy', 'yz', 'zx'])
        self.cbox_plot_axis = ttk.Combobox(self.frm_plotwindow, values=['x', 'y', 'z'])
        self.cbox_B_axes = ttk.Combobox(self.frm_plotwindow, values=['Bx', 'By', 'Bz'])
        self.cbox_scan_direction = ttk.Combobox(self.frm_plotwindow, values=['x', 'y', 'z'])
        self.ent_z_location = ttk.Entry(self.frm_plotwindow)
        self.cbox_scan_spacing = ttk.Combobox(self.frm_plotwindow, values=['0.1', '0.25', '0.5', '1.0', '2.0'])

        self.btn_load_data = ttk.Button(self.frm_plotwindow, text='Load Data', command=self.load_data)
        self.btn_plot = ttk.Button(self.frm_plotwindow, text='Plot Data', command=self.generate_plots)

        self.lbl_scan_plane.grid(row=0, column=0)
        self.lbl_plot_axis.grid(row=1, column=0)
        self.lbl_B_axis.grid(row=2, column=0)
        self.lbl_scan_direction.grid(row=3, column=0)
        self.lbl_scan_spacing.grid(row=4, column=0)
        self.lbl_z_location.grid(row=5, column=0)
        self.cbox_scan_plane.grid(row=0, column=1)
        self.cbox_plot_axis.grid(row=1, column=1)
        self.cbox_B_axes.grid(row=2, column=1)
        self.cbox_scan_direction.grid(row=3, column=1)
        self.cbox_scan_spacing.grid(row=4, column=1)
        self.ent_z_location.grid(row=5, column=1)
        self.btn_load_data.grid(row=6, column=0)
        self.btn_plot.grid(row=6, column=1)

    def load_data(self):
        filename = tk.filedialog.askopenfilename(initialdir='./scans/', title='Select Data File', filetypes=(('Text Files', '*.txt'), ('All Files', '*.*')))
        self.data = np.loadtxt(filename)
    
    def generate_plots(self):
        # Get data from comboboxes
        plane = self.cbox_scan_plane.get()
        plot_axis = self.cbox_plot_axis.get()
        B_axis = self.cbox_B_axes.get()
        scan_direction = self.cbox_scan_direction.get()
        z_location = float(self.ent_z_location.get())
        scan_spacing = float(self.cbox_scan_spacing.get())
        # Create plots
        self.plot_dashboard = PlotDashboard()
        # Use inputs to generate plots
        self.plot_dashboard.plot_data(self.data, plane, plot_axis, B_axis, scan_direction, scan_spacing, z_location)

class PlotDashboard:
    plane_index = {'xy': (0, 1, 'x axis [mm]', 'y axis[mm]'),
                   'yz': (1, 2, 'y axis [mm]', 'z axis [mm]'),
                   'zx': (2, 0, 'z axis [mm]', 'x axis [mm]')}
    int_across_index = {'x': 0, 'y': 1, 'z': 2}
    args_index = {'x': 0, 'y': 1, 'z': 2, 'Bx': 3, 'By': 4, 'Bz': 5}
    def __init__(self):
        pass

    def create_figs(self):
        self.fig_p1 = plt.figure(figsize=(11, 8.5))
        self.fig_p2 = plt.figure(figsize=(11, 8.5))
        self.fig_p1.suptitle('3D Plots')
        self.fig_p2.suptitle('2D Plots')
        self.fig_p2.subplots_adjust(hspace=0.3)
    
    def create_subplots(self):
        # 3D plots - Page 1
        self.abs_3d = self.fig_p1.add_subplot(221, projection='3d')
        self.abs_3d.set_title('Absolute value')
        self.abs_3d.set_xlabel(self.plane_index[self.plane][2])
        self.abs_3d.set_ylabel(self.plane_index[self.plane][3])
        self.abs_3d.set_zlabel('B [mT]')
        self.bx_3d = self.fig_p1.add_subplot(222, projection='3d')
        self.bx_3d.set_title('Bx')
        self.bx_3d.set_xlabel(self.plane_index[self.plane][2])
        self.bx_3d.set_ylabel(self.plane_index[self.plane][3])
        self.bx_3d.set_zlabel('Bx [mT]')
        self.by_3d = self.fig_p1.add_subplot(223, projection='3d')
        self.by_3d.set_title('By')
        self.by_3d.set_xlabel(self.plane_index[self.plane][2])
        self.by_3d.set_ylabel(self.plane_index[self.plane][3])
        self.by_3d.set_zlabel('By [mT]')
        self.bz_3d = self.fig_p1.add_subplot(224, projection='3d')
        self.bz_3d.set_title('Bz')
        self.bz_3d.set_xlabel(self.plane_index[self.plane][2])
        self.bz_3d.set_ylabel(self.plane_index[self.plane][3])
        self.bz_3d.set_zlabel('Bz [mT]')
        # 2D plots - Page 2
        self.plot_221 = self.fig_p2.add_subplot(221)
        self.plot_221.set_title('')
        self.plot_222 = self.fig_p2.add_subplot(222)
        self.plot_222.set_title('')
        self.plot_223 = self.fig_p2.add_subplot(223)
        self.plot_223.set_title('')
        self.plot_224 = self.fig_p2.add_subplot(224)
        self.plot_224.set_title('')
    
    def generate_header(self):
        # placeholder for reading text input values from gui
        self.header = 'AQD-0024\n'+\
                      'Scan size x: 30 y: 0 z: 343.4\n'+\
                      'Current: 0.0A'
        self.bbox_props = dict(boxstyle='round', facecolor='grey', alpha=0.3)
    
    def plot_data(self, data, plane, plot_axis, B_axis, scan_direction, scan_spacing, z_location):
        args = [data, plane, plot_axis, B_axis, scan_direction, scan_spacing, z_location]
        self.data_3d = data
        self.generate_2d_plot_221(*args)
        

    def plot_3d_abs(self):
        Bxyz_abs = np.linalg.norm(self.data_3d[:, 3:], axis=1)
        # Place text boxes containing header information
        self.fig_p1.text(0.03, 0.97, self.header, verticalalignment='top', bbox=self.bbox_props)
        self.fig_p2.text(0.03, 0.97, self.header, verticalalignment='top', bbox=self.bbox_props)
        # Plot 3d Absolute values
        self.abs_3d.scatter(self.data_3d[:, self.plane_index[self.plane][0]], self.data_3d[:, self.plane_index[self.plane][1]], Bxyz_abs,
                            marker='.', cmap='rainbow', c=Bxyz_abs)
        # Add colorbar
        self.fig_p1.colorbar(self.abs_3d.collections[0], ax=self.abs_3d, pad=0.2)
    
    def plot_3d_bx(self):
        # Plot 3d Bx
        self.bx_3d.scatter(self.data_3d[:, self.plane_index[self.plane][0]], self.data_3d[:, self.plane_index[self.plane][1]], self.data_3d[:, 3],
                           marker='.', cmap='rainbow', c=self.data_3d[:, 3])
        # Add colorbar
        self.fig_p1.colorbar(self.bx_3d.collections[0], ax=self.bx_3d, pad=0.2)
    
    def plot_3d_by(self):
        # Plot 3d By
        self.by_3d.scatter(self.data_3d[:, self.plane_index[self.plane][0]], self.data_3d[:, self.plane_index[self.plane][1]], self.data_3d[:, 4],
                           marker='.', cmap='rainbow', c=self.data_3d[:, 4])
        # Add colorbar
        self.fig_p1.colorbar(self.by_3d.collections[0], ax=self.by_3d, pad=0.2)
    
    def plot_3d_bz(self):
        # Plot 3d Bz
        self.bz_3d.scatter(self.data_3d[:, self.plane_index[self.plane][0]], self.data_3d[:, self.plane_index[self.plane][1]], self.data_3d[:, 5],
                           marker='.', cmap='rainbow', c=self.data_3d[:, 5])
        # Add colorbar
        self.fig_p1.colorbar(self.bz_3d.collections[0], ax=self.bz_3d, pad=0.2)

    def generate_2d_plot_221(self, *args):
        data, plane, plot_axis, B_axis, scan_direction, scan_spacing, z_location = args
        data_at_z = data[(data[:, self.args_index[scan_direction]] > z_location-scan_spacing/2)&(data[:, self.args_index[scan_direction]] < z_location+scan_spacing/2)]
        self.plot_221.plot(data_at_z[:, self.args_index[plot_axis]], data_at_z[:, self.args_index[B_axis]], label=f'{B_axis} at {z_location} mm')
        self.plot_221.set_xlabel(f'{plot_axis} axis [mm] at z={z_location} mm')
        self.plot_221.set_ylabel(f'{B_axis} [mT]')
        self.plot_221.grid()
    
    def generate_2d_plot_222(self, *args):
        bxyz_index = {'Bx': 3, 'By': 4, 'Bz': 5}
        b_keys = list(bxyz_index.keys())
        b_values = list(bxyz_index.values())
        data, plane, plot_axis, B_axis, scan_direction, scan_spacing, z_location = args
        next_b_index = b_keys.index(B_axis)-1
        data_at_z = data[(data[:, self.args_index[scan_direction]] > z_location-scan_spacing/2)&(data[:, self.args_index[scan_direction]] < z_location+scan_spacing/2)]
        self.plot_222.plot(data_at_z[:, self.args_index[plot_axis]], data_at_z[:, b_values[next_b_index]], label=f'{b_keys[next_b_index]} at z={z_location} mm')
        self.plot_222.set_xlabel(f'{plot_axis} axis [mm] at z={z_location} mm')
        self.plot_222.set_ylabel(f'{b_keys[next_b_index]} [mT]')
        self.plot_222.grid()

    
    def show_plots(self):
        plt.show()

if __name__ == '__main__':
    root = tk.Tk()
    pw = PlotWindow(root)
    root.mainloop()
    # data = np.genfromtxt('area.txt')
    # plot = PlotDashboard()
    # plot.plot_data(data, 'zx')
    # plot.show_plots()