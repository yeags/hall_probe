import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os
import pickle
np.set_printoptions(suppress=True)

def integrate_lines_from_area(data: np.ndarray, scan_plane: str, scan_direction: str, scan_spacing: float):
    '''
    data: numpy array (x, y, z, Bx, By, Bz)
    scan_plane: str 'xy', 'yz', 'zx'
    scan_direction: str 'x', 'y', 'z'
    scan_spacing: float (eg. 1.0)
    returns (n, 4) array of Bxyz integrals of each scan line
    '''
    plane_step_across_dict = {'xy': {'x': 1, 'y': 0}, 'yz': {'y': 2, 'z': 1}, 'zx': {'z': 0, 'x': 2}}
    integration_dict = {'x': 0, 'y': 1, 'z': 2, 'Bx': 3, 'By': 4, 'Bz': 5}
    data_int_min = np.min(data[:, plane_step_across_dict[scan_plane][scan_direction]])
    data_int_max = np.max(data[:, plane_step_across_dict[scan_plane][scan_direction]])
    steps = np.arange(round(data_int_min, 2), round(data_int_max,2) + scan_spacing, scan_spacing)
    integrals = np.zeros((steps.shape[0], 4))
    for j, step in enumerate(steps):
        line = data[(data[:, plane_step_across_dict[scan_plane][scan_direction]] > step - scan_spacing / 2) & (data[:, plane_step_across_dict[scan_plane][scan_direction]] < step + scan_spacing / 2)]
        dx_array = np.zeros((line.shape[0], 3))
        for i in range(1, line.shape[0]):
            dx = line[i, integration_dict[scan_direction]] - line[i - 1, integration_dict[scan_direction]]
            dx_array[i-1] = dx * (line[i, 3:] + line[i-1, 3:]) / 2
        dx_array_integrals = np.sum(dx_array, axis=0)
        integrals[j] = np.hstack((step, dx_array_integrals))
    return integrals
        

class PlotWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title = 'Plotting Parameters'
        self.frm_plotwindow = ttk.Frame(self)
        self.frm_plotwindow.pack()
        self.create_widgets()
    
    def create_widgets(self):
        self.lbl_scan_plane = ttk.Label(self.frm_plotwindow, text='Scan Plane')
        self.lbl_plot_axis = ttk.Label(self.frm_plotwindow, text='Plot Axis')
        self.lbl_int_from = ttk.Label(self.frm_plotwindow, text='Integrate From')
        self.lbl_int_to = ttk.Label(self.frm_plotwindow, text='To')
        self.lbl_scan_direction = ttk.Label(self.frm_plotwindow, text='Scan Direction')
        self.lbl_scan_spacing = ttk.Label(self.frm_plotwindow, text='Scan Spacing [mm]')
        
        self.cbox_scan_plane = ttk.Combobox(self.frm_plotwindow, values=['xy', 'yz', 'zx'], width=6)
        self.cbox_scan_plane.current(2)
        self.cbox_plot_axis = ttk.Combobox(self.frm_plotwindow, values=['x', 'y', 'z'], width=6)
        self.cbox_plot_axis.current(0)
        self.cbox_scan_direction = ttk.Combobox(self.frm_plotwindow, values=['x', 'y', 'z'], width=6)
        self.cbox_scan_direction.current(2)
        self.cbox_scan_spacing = ttk.Combobox(self.frm_plotwindow, values=['0.1', '0.25', '0.5', '1.0', '2.0'], width=6)
        self.cbox_scan_spacing.current(3)

        self.ent_int_from = ttk.Entry(self.frm_plotwindow, width=6)
        self.ent_int_from.insert(0, '-11')
        self.ent_int_to = ttk.Entry(self.frm_plotwindow, width=6)
        self.ent_int_to.insert(0, '11')

        self.btn_load_data = ttk.Button(self.frm_plotwindow, text='Load Data', command=self.load_data)
        self.btn_plot = ttk.Button(self.frm_plotwindow, text='Plot Data', command=self.generate_plots, state=tk.DISABLED)
        # place widgets
        self.lbl_scan_plane.grid(row=0, column=0, sticky='e')
        self.lbl_plot_axis.grid(row=1, column=0, sticky='e')
        self.lbl_int_from.grid(row=2, column=0, sticky='e')
        self.lbl_int_to.grid(row=2, column=2, sticky='e')
        self.lbl_scan_direction.grid(row=3, column=0, sticky='e')
        self.lbl_scan_spacing.grid(row=4, column=0, sticky='e')
        self.cbox_scan_plane.grid(row=0, column=1, sticky='w', padx=5, pady=5)
        self.cbox_plot_axis.grid(row=1, column=1, sticky='w', padx=5, pady=5)
        self.ent_int_from.grid(row=2, column=1, sticky='w', padx=5, pady=5)
        self.ent_int_to.grid(row=2, column=3, sticky='w', padx=5, pady=5)
        self.cbox_scan_direction.grid(row=3, column=1, sticky='w', padx=5, pady=5)
        self.cbox_scan_spacing.grid(row=4, column=1, sticky='w', padx=5, pady=5)
        self.btn_load_data.grid(row=5, column=0, padx=5, pady=5)
        self.btn_plot.grid(row=5, column=1, padx=5, pady=5)

    def load_data(self):
        filename = filedialog.askopenfilename(initialdir='./scans/', title='Select Data File', filetypes=(('Text Files', '*.txt'), ('All Files', '*.*')))
        self.data = np.genfromtxt(filename)
        self.filepath = os.path.dirname(filename)
        # Convert mm to cm and mT to G
        self.data[:, :3] /= 10
        self.data[:, 3:] *= 10
        self.btn_plot.config(state=tk.NORMAL)
    
    def get_inputs(self):
        scan_plane = self.cbox_scan_plane.get()
        plot_axis = self.cbox_plot_axis.get()
        scan_direction = self.cbox_scan_direction.get()
        scan_spacing = float(self.cbox_scan_spacing.get())
        int_from_to = (float(self.ent_int_from.get()), float(self.ent_int_to.get()))
        return scan_plane, plot_axis, int_from_to, scan_direction, scan_spacing
    
    def generate_plots(self):
        # Get data from comboboxes
        self.get_inputs()
        # Create dashboard instance and pass arguments
        self.plot_dashboard = PlotDashboard(self.data, self.filepath, *self.get_inputs())
        self.plot_dashboard.save_plots()
        self.plot_dashboard.show_plots()

class PlotDashboard:
    plane_index = {'xy': (0, 1, 'x axis [cm]', 'y axis[cm]'),
                   'yz': (1, 2, 'y axis [cm]', 'z axis [cm]'),
                   'zx': (2, 0, 'z axis [cm]', 'x axis [cm]')}
    int_across_index = {'x': 0, 'y': 1, 'z': 2}
    args_index = {'x': 0, 'y': 1, 'z': 2, 'Bx': 3, 'By': 4, 'Bz': 5}
    integrals_index = {'x': 0, 'Bx': 1, 'By': 2, 'Bz': 3}
    coeffs_header = ['Bx', 'By', 'I Bx', 'I By']

    def __init__(self, data, filepath, scan_plane, plot_axis, int_from_to, scan_direction, scan_spacing):
        self.data = data
        self.filepath = filepath
        self.scan_plane = scan_plane
        self.plot_axis = plot_axis
        self.int_from_to = (int_from_to[0] / 10, int_from_to[1] / 10)
        self.scan_direction = scan_direction
        self.scan_spacing = scan_spacing / 10
        self.data_at_z = self.data[(self.data[:, self.args_index[self.scan_direction]] > 0-self.scan_spacing/2)&(self.data[:, self.args_index[self.scan_direction]] < 0+self.scan_spacing/2)]
        self.z_location = np.mean(self.data_at_z[:, 2])
        self.data_at_z_by_fit = np.polyfit(self.data_at_z[:, 0], self.data_at_z[:, 4], 1)
        self.scan_integrals = integrate_lines_from_area(self.data[(self.data[:, 0] > self.int_from_to[0]-self.scan_spacing/2) & (self.data[:, 0] < self.int_from_to[1]+self.scan_spacing/2)], self.scan_plane, self.scan_direction, self.scan_spacing)
        self.coeffs_bx = np.polyfit(self.data_at_z[:, 0], self.data_at_z[:, 3], 9)
        self.coeffs_by = np.polyfit(self.data_at_z[:, 0], self.data_at_z[:, 4], 9)
        self.coeffs_ibx = np.polyfit(self.scan_integrals[:, 0], self.scan_integrals[:, 1], 9)
        self.coeffs_iby = np.polyfit(self.scan_integrals[:, 0], self.scan_integrals[:, 2], 9)
        self.all_coeffs = np.flip(np.vstack((self.coeffs_bx, self.coeffs_by, self.coeffs_ibx, self.coeffs_iby)).T, axis=0).round(1)
        self.integrated_magnetic_value = self.coeffs_iby[8]
        self.magnetic_length = self.coeffs_iby[8] / self.coeffs_by[8]
        self.offset = (self.coeffs_ibx[-1] / self.coeffs_ibx[-2] / 10, self.coeffs_iby[-1] / self.coeffs_iby[-2] / 10)
        self.generate_header()
        self.create_figs()
        self.create_subplots()
        self.populate_dashboard()
    
    def create_figs(self):
        self.fig_p1 = plt.figure(figsize=(11, 8.5))
        self.fig_p2 = plt.figure(figsize=(11, 8.5))
        self.fig_p1.suptitle('3D Plots')
        self.fig_p2.suptitle('2D Plots')
        self.fig_p2.subplots_adjust(hspace=0.37, wspace=0.3,left=0.1, right=0.95, top=0.9, bottom=0.05)
    
    def save_plots(self):
        # Save plots as pdf docs
        self.fig_p1.savefig(self.filepath + '/3d_plots.pdf')
        self.fig_p2.savefig(self.filepath + '/2d_plots.pdf')
    
    def create_subplots(self):
        # 3D plots - Page 1
        self.abs_3d = self.fig_p1.add_subplot(221, projection='3d')
        self.abs_3d.set_title('Absolute value')
        self.abs_3d.set_xlabel(self.plane_index[self.scan_plane][2])
        self.abs_3d.set_ylabel(self.plane_index[self.scan_plane][3])
        self.abs_3d.set_zlabel('B [G]')
        self.bx_3d = self.fig_p1.add_subplot(222, projection='3d')
        self.bx_3d.set_title('Bx')
        self.bx_3d.set_xlabel(self.plane_index[self.scan_plane][2])
        self.bx_3d.set_ylabel(self.plane_index[self.scan_plane][3])
        self.bx_3d.set_zlabel('Bx [G]')
        self.by_3d = self.fig_p1.add_subplot(223, projection='3d')
        self.by_3d.set_title('By')
        self.by_3d.set_xlabel(self.plane_index[self.scan_plane][2])
        self.by_3d.set_ylabel(self.plane_index[self.scan_plane][3])
        self.by_3d.set_zlabel('By [G]')
        self.bz_3d = self.fig_p1.add_subplot(224, projection='3d')
        self.bz_3d.set_title('Bz')
        self.bz_3d.set_xlabel(self.plane_index[self.scan_plane][2])
        self.bz_3d.set_ylabel(self.plane_index[self.scan_plane][3])
        self.bz_3d.set_zlabel('Bz [G]')
        # 2D plots - Page 2
        self.plot_321 = self.fig_p2.add_subplot(321)
        self.plot_321.set_title('By')
        self.plot_322 = self.fig_p2.add_subplot(322)
        self.plot_322.set_title('Bx')
        self.plot_323 = self.fig_p2.add_subplot(323)
        self.plot_323.set_title('By Integrals')
        self.plot_324 = self.fig_p2.add_subplot(324)
        self.plot_324.set_title('Bx Integrals')
        # Table
        self.coeffs_table = self.fig_p2.add_subplot(325)
        self.coeffs_table.axis('tight')
        self.coeffs_table.set_axis_off()
        # Text Info Box
        self.text_info = self.fig_p2.add_subplot(326)
        self.text_info.axis('tight')
        self.text_info.set_axis_off()

    
    def generate_header(self):
        xyz_min = np.min(self.data[:, :3], axis=0)
        xyz_max = np.max(self.data[:, :3], axis=0)
        xyz_range = np.round(xyz_max - xyz_min, 2)
        with open(self.filepath+'/magnet_info.pkl', 'rb') as f:
            self.magnet_info = pickle.load(f)
        self.header = f'{self.magnet_info[0]}-{self.magnet_info[1]}\nScan Volume: x: {xyz_range[0]} y: {xyz_range[1]} z: {xyz_range[2]} cm\nCurrent: {self.magnet_info[2]} A'
        self.bbox_props = dict(boxstyle='round', facecolor='grey', alpha=0.3)
    
    def populate_dashboard(self):
        # Populate 3D subplots
        self.plot_3d_abs()
        self.plot_3d_bx()
        self.plot_3d_by()
        self.plot_3d_bz()
        # Populate 2d subplots
        self.generate_2d_plot_321()
        self.generate_2d_plot_322()
        self.generate_2d_plot_323()
        self.generate_2d_plot_324()
        self.generate_table()
        self.generate_text_info()

    def plot_3d_abs(self):
        Bxyz_abs = np.linalg.norm(self.data[:, 3:], axis=1)
        # Place text boxes containing header information
        self.fig_p1.text(0.01, 0.99, self.header, verticalalignment='top', bbox=self.bbox_props)
        self.fig_p2.text(0.01, 0.99, self.header, verticalalignment='top', bbox=self.bbox_props)
        # Plot 3d Absolute values
        self.abs_3d.scatter(self.data[:, self.plane_index[self.scan_plane][0]], self.data[:, self.plane_index[self.scan_plane][1]], Bxyz_abs,
                            marker='.', cmap='rainbow', c=Bxyz_abs)
        # Add colorbar
        self.fig_p1.colorbar(self.abs_3d.collections[0], ax=self.abs_3d, pad=0.2)
    
    def plot_3d_bx(self):
        # Plot 3d Bx
        self.bx_3d.scatter(self.data[:, self.plane_index[self.scan_plane][0]], self.data[:, self.plane_index[self.scan_plane][1]], self.data[:, 3],
                           marker='.', cmap='rainbow', c=self.data[:, 3])
        # Add colorbar
        self.fig_p1.colorbar(self.bx_3d.collections[0], ax=self.bx_3d, pad=0.2)
    
    def plot_3d_by(self):
        # Plot 3d By
        self.by_3d.scatter(self.data[:, self.plane_index[self.scan_plane][0]], self.data[:, self.plane_index[self.scan_plane][1]], self.data[:, 4],
                           marker='.', cmap='rainbow', c=self.data[:, 4])
        # Add colorbar
        self.fig_p1.colorbar(self.by_3d.collections[0], ax=self.by_3d, pad=0.2)
    
    def plot_3d_bz(self):
        # Plot 3d Bz
        self.bz_3d.scatter(self.data[:, self.plane_index[self.scan_plane][0]], self.data[:, self.plane_index[self.scan_plane][1]], self.data[:, 5],
                           marker='.', cmap='rainbow', c=self.data[:, 5])
        # Add colorbar
        self.fig_p1.colorbar(self.bz_3d.collections[0], ax=self.bz_3d, pad=0.2)

    def generate_2d_plot_321(self):
        self.plot_321.plot(self.data_at_z[:, self.args_index[self.plot_axis]], self.data_at_z[:, self.args_index['By']], marker='.', label=f'By at z={self.z_location:.3f} cm')
        self.plot_321.set_xlabel(f'{self.plot_axis} axis [cm] at z={self.z_location:.3f} cm')
        self.plot_321.set_ylabel('By [G]')
        self.plot_321.grid()
    
    def generate_2d_plot_322(self):
        self.plot_322.plot(self.data_at_z[:, self.args_index[self.plot_axis]], self.data_at_z[:, self.args_index['Bx']], marker='.', label=f'Bx at z={self.z_location:.3f} cm')
        self.plot_322.set_xlabel(f'{self.plot_axis} axis [cm] at z={self.z_location:.3f} cm')
        self.plot_322.set_ylabel('Bx [G]')
        self.plot_322.grid()

    def generate_2d_plot_323(self):
        self.plot_323.plot(self.scan_integrals[:, 0], self.scan_integrals[:, self.integrals_index['By']], marker='.', label='By Integrals')
        self.plot_323.set_xlabel('x axis [cm]')
        self.plot_323.set_ylabel('By [G$\cdot$cm]')
        self.plot_323.grid()
        
    def generate_2d_plot_324(self):
        self.plot_324.plot(self.scan_integrals[:, 0], self.scan_integrals[:, self.integrals_index['Bx']], marker='.', label='Bx Integrals')
        self.plot_324.set_xlabel('x axis [cm]')
        self.plot_324.set_ylabel('Bx [G$\cdot$cm]')
        self.plot_324.grid()
    
    def generate_table(self):
        # Plot table of self.all_coeffs
        t = self.coeffs_table.table(cellText=self.all_coeffs, colLabels=self.coeffs_header, rowLabels=[1,2,3,4,5,6,7,8,9,10], loc='center')
        t.auto_set_font_size(False)
        t.set_fontsize(12)
        t.scale(1, 1.2)

    def generate_text_info(self):
        # Generate text information
        info = '\n'.join((f'Integrated Quadrupole: {self.integrated_magnetic_value:.1f} G',
                          f'Magnetic Length: {self.magnetic_length:.1f} cm',
                          f'Offset: $\Delta$x: {self.offset[0]:.3f} mm $\Delta$y: {self.offset[1]:.3f} mm'))
        self.fig_p2.text(0.6, 0.25, info, verticalalignment='top', bbox=self.bbox_props)

    def show_plots(self):
        plt.show()

if __name__ == '__main__':
    root = tk.Tk()
    pw = PlotWindow(root)
    root.mainloop()