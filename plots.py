import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os
import pickle
import beamcalc as bc
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
        self.frm_quad_plot = ttk.LabelFrame(self, text='Quadrupole Plotting')
        self.frm_dipole_plot = ttk.LabelFrame(self, text='Dipole Plotting')
        self.geometry('520x300')
        self.frm_quad_plot.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        self.frm_dipole_plot.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        self.create_widgets()
    
    def create_widgets(self):
        self.btn_quad_load_data = ttk.Button(self.frm_quad_plot, text='Load Data',
                                             command=self.load_data)
        self.btn_quad_plot = ttk.Button(self.frm_quad_plot, text='Plot Data',
                                        command=self.generate_plots, state=tk.DISABLED)
        self.btn_dipole_load_data = ttk.Button(self.frm_dipole_plot, text='Load Data',
                                               command=lambda: self.load_data(convert_to_gauss=False))
        self.btn_dipole_plot = ttk.Button(self.frm_dipole_plot, text='Plot Data',
                                          command=lambda: self.generate_plots(mag_type='dipole'), state=tk.DISABLED)
        self.lbl_dp_x_pos = ttk.Label(self.frm_dipole_plot, text='X Position (mm)', justify=tk.RIGHT)
        self.ent_dp_x_pos = ttk.Entry(self.frm_dipole_plot, width=6)
        self.lbl_dp_y_pos = ttk.Label(self.frm_dipole_plot, text='Y Position (mm)', justify=tk.RIGHT)
        self.ent_dp_y_pos = ttk.Entry(self.frm_dipole_plot, width=6)
        self.lbl_dp_z_pos = ttk.Label(self.frm_dipole_plot, text='Z Position (mm)', justify=tk.RIGHT)
        self.ent_dp_z_pos = ttk.Entry(self.frm_dipole_plot, width=6)
        self.lbl_dp_z_max = ttk.Label(self.frm_dipole_plot, text='Z Max Position (mm)', justify=tk.RIGHT)
        self.ent_dp_z_max = ttk.Entry(self.frm_dipole_plot, width=6)
        self.lbl_dp_angle = ttk.Label(self.frm_dipole_plot, text='Bend Angle (degrees)', justify=tk.RIGHT)
        self.ent_dp_angle = ttk.Entry(self.frm_dipole_plot, width=6)
        self.lbl_dp_x_min = ttk.Label(self.frm_dipole_plot, text='X Min (mm)', justify=tk.RIGHT)
        self.ent_dp_x_min = ttk.Entry(self.frm_dipole_plot, width=6)
        self.lbl_dp_x_max = ttk.Label(self.frm_dipole_plot, text='X Max (mm)', justify=tk.RIGHT)
        self.ent_dp_x_max = ttk.Entry(self.frm_dipole_plot, width=6)
        self.lbl_dp_b_rho = ttk.Label(self.frm_dipole_plot, text='Beam Rigidity (T-m)', justify=tk.RIGHT)
        self.ent_dp_b_rho = ttk.Entry(self.frm_dipole_plot, width=6)
        self.lbl_dp_z_step = ttk.Label(self.frm_dipole_plot, text='Z Step (mm)', justify=tk.RIGHT)
        self.ent_dp_z_step = ttk.Entry(self.frm_dipole_plot, width=6)
        # place widgets
        self.btn_quad_load_data.grid(row=5, column=0, padx=5, pady=5)
        self.btn_quad_plot.grid(row=5, column=1, padx=5, pady=5)
        self.btn_dipole_load_data.grid(row=5, column=0, padx=5, pady=5)
        self.btn_dipole_plot.grid(row=5, column=2, padx=5, pady=5)
        self.lbl_dp_x_pos.grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.ent_dp_x_pos.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        self.lbl_dp_y_pos.grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.ent_dp_y_pos.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        self.lbl_dp_z_pos.grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.ent_dp_z_pos.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        self.lbl_dp_z_max.grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.ent_dp_z_max.grid(row=3, column=1, padx=5, pady=5, sticky='w')
        self.lbl_dp_angle.grid(row=4, column=0, padx=5, pady=5, sticky='e')
        self.ent_dp_angle.grid(row=4, column=1, padx=5, pady=5, sticky='w')
        self.lbl_dp_x_min.grid(row=0, column=2, padx=5, pady=5, sticky='e')
        self.ent_dp_x_min.grid(row=0, column=3, padx=5, pady=5, sticky='w')
        self.lbl_dp_x_max.grid(row=0, column=4, padx=5, pady=5, sticky='e')
        self.ent_dp_x_max.grid(row=0, column=5, padx=5, pady=5, sticky='w')
        self.lbl_dp_z_step.grid(row=2, column=2, padx=5, pady=5, sticky='e')
        self.ent_dp_z_step.grid(row=2, column=3, padx=5, pady=5, sticky='w')
        self.lbl_dp_b_rho.grid(row=1, column=2, padx=5, pady=5, sticky='e')
        self.ent_dp_b_rho.grid(row=1, column=3, padx=5, pady=5, sticky='w')
        self.ent_dp_angle.insert(0, '10')
        self.ent_dp_z_step.insert(0, '0.5')

    def load_data(self, convert_to_gauss=True):
        filename = filedialog.askopenfilename(initialdir='./scans/', title='Select Data File',
                                              filetypes=(('Text Files', '*.txt'), ('All Files', '*.*')))
        self.data = np.genfromtxt(filename)
        self.filepath = os.path.dirname(filename)
        print(f'filename: {filename}\nfilepath: {self.filepath}')
        if convert_to_gauss:
            # Convert mm to cm and mT to G
            self.data[:, :3] /= 10
            self.data[:, 3:] *= 10
            self.btn_quad_plot.config(state=tk.NORMAL)
        else:
            self.btn_dipole_plot.config(state=tk.NORMAL)
    
    def generate_plots(self, mag_type='quadrupole'):
        if mag_type == 'quadrupole'.lower():
            # Create dashboard instance and pass arguments
            self.plot_dashboard = QuadPlotDashboard(self.data, self.filepath)
            self.plot_dashboard.save_plots()
            self.plot_dashboard.show_plots()
        elif mag_type == 'dipole'.lower():
            self.dipole_plot_dashboard = DipolePlotDashboard(self.data, self.filepath)

class QuadPlotDashboard:
    plane_index = {'xy': (0, 1, 'x axis [cm]', 'y axis[cm]'),
                   'yz': (1, 2, 'y axis [cm]', 'z axis [cm]'),
                   'zx': (2, 0, 'z axis [cm]', 'x axis [cm]')}
    args_index = {'x': 0, 'y': 1, 'z': 2, 'Bx': 3, 'By': 4, 'Bz': 5}
    integrals_index = {'x': 0, 'Bx': 1, 'By': 2, 'Bz': 3}
    coeffs_header = ['Bx', 'By', '$\int$ Bx', '$\int$ By']
    coefficient_index = {'xy': None, 'yz': (1, 0, 3, 2), 'zx': (0, 1, 2, 3)}

    def __init__(self, data, filepath):
        self.data = data
        self.filepath = filepath
        self.find_scan_parameters(self.data[:, :3])
        self.perform_fit()
        self.generate_header()
        self.create_figs()
        self.create_subplots()
        self.populate_dashboard()

    def find_scan_parameters(self, xyz):
        '''
        Fit plane to data and determine scan plane
        '''
        planes = ['yz', 'zx', 'xy']
        x, y, z = xyz[:, 0], xyz[:, 1], xyz[:, 2]
        A = np.array([[np.sum(x**2), np.sum(x*y), np.sum(x)],
              [np.sum(x*y), np.sum(y**2), np.sum(y)],
              [np.sum(x), np.sum(y), xyz.shape[0]]])
        b = np.array([np.sum(x*z), np.sum(y*z), np.sum(z)])
        v = np.dot(np.linalg.inv(A), b)
        v_hat = v / np.linalg.norm(v)
        p_arg = planes[np.argmax(np.abs(v_hat))]
        '''
        Determine scan area and find longest scanned axis for scan direction
        '''
        scan_direction = ['x', 'y', 'z']
        scan_range = np.max(xyz, axis=0) - np.min(xyz, axis=0)
        scan_dir_arg = scan_direction[np.argmax(scan_range)]
        '''
        Determine scan spacing from scan plane
        '''
        plane_index = {'xy': (0, 1), 'yz': (1, 2), 'zx': (2, 0)}
        delta_a = np.diff(xyz[:, plane_index[p_arg][0]])
        delta_b = np.diff(xyz[:, plane_index[p_arg][1]])
        dist = np.sqrt(delta_a**2 + delta_b**2)
        dist_std = np.std(dist, ddof=1)
        spacing = np.round(dist[(dist > -dist_std) & (dist < dist_std)].mean(), 3)
        '''
        Determine plot axis
        '''
        plot_axis = ''.join([i for i in p_arg if i not in scan_dir_arg])
        '''
        Determine integration range
        '''
        int_across_index = {'x': 0, 'y': 1, 'z': 2}
        range_tuple = (np.min(xyz[:, int_across_index[plot_axis]]), np.max(xyz[:, int_across_index[plot_axis]]))
        '''
        Assign class variables
        '''
        self.scan_plane = p_arg
        self.plot_axis = plot_axis
        self.scan_direction = scan_dir_arg
        self.scan_spacing = spacing
        self.int_from_to = range_tuple
        # Print scan parameters
        print(f'Scan Plane: {self.scan_plane}\nPlot Axis: {self.plot_axis}\nScan Direction: {self.scan_direction}\
              \nScan Spacing: {self.scan_spacing} cm\nIntegrate From: {self.int_from_to[0]} cm\nIntegrate To: {self.int_from_to[1]} cm')
    

    def perform_fit(self):
        self.data_at_z = self.data[(self.data[:, self.args_index[self.scan_direction]] > -self.scan_spacing/2)&(self.data[:, self.args_index[self.scan_direction]] < self.scan_spacing/2)]
        self.z_location = np.mean(self.data_at_z[:, 2])
        self.scan_integrals = integrate_lines_from_area(self.data[(self.data[:, self.args_index[self.plot_axis]] > self.int_from_to[0]-self.scan_spacing/2) & (self.data[:, self.args_index[self.plot_axis]] < self.int_from_to[1]+self.scan_spacing/2)], self.scan_plane, self.scan_direction, self.scan_spacing)
        self.coeffs_bx = np.polyfit(self.data_at_z[:, self.args_index[self.plot_axis]], self.data_at_z[:, 3], 9)
        self.coeffs_by = np.polyfit(self.data_at_z[:, self.args_index[self.plot_axis]], self.data_at_z[:, 4], 9)
        self.coeffs_ibx = np.polyfit(self.scan_integrals[:, 0], self.scan_integrals[:, 1], 9)
        self.coeffs_iby = np.polyfit(self.scan_integrals[:, 0], self.scan_integrals[:, 2], 9)
        self.all_coeffs = np.flip(np.vstack((self.coeffs_bx, self.coeffs_by, self.coeffs_ibx, self.coeffs_iby)).T, axis=0).round(1)
        '''
        Calculate integrated magnetic value, magnetic length, and offset
        taking into account the scan parameters (horizontal or vertical plane)
        '''
        self.integrated_magnetic_value = self.all_coeffs[1, self.coefficient_index[self.scan_plane][3]]
        self.quadrupole_magnetic_length = self.all_coeffs[1, self.coefficient_index[self.scan_plane][3]] / self.all_coeffs[1, self.coefficient_index[self.scan_plane][1]]
        dml_numerator = self.scan_integrals[(self.scan_integrals[:, 0] > -self.scan_spacing / 2) & (self.scan_integrals[:, 0] < self.scan_spacing / 2)]
        dml_denominator = self.data_at_z[(self.data_at_z[:, 0] > -self.scan_spacing / 2) & (self.data_at_z[:, 0] < self.scan_spacing / 2)]
        self.dipole_magnetic_length = dml_numerator[0][2] / dml_denominator[0][4]
        # print(f'dml_numerator shape: {self.dml_numerator.shape}\ndml_denominator shape: {self.dml_denominator.shape}')
        # print(f'dml_numerator: {self.dml_numerator}\ndml_denominator: {self.dml_denominator}')
        print(f'dml: {self.dipole_magnetic_length:.3f} cm')
        self.offset = (self.all_coeffs[0, self.coefficient_index[self.scan_plane][3]] / self.all_coeffs[1, self.coefficient_index[self.scan_plane][3]] * 10, self.all_coeffs[0, self.coefficient_index[self.scan_plane][2]] / self.all_coeffs[1, self.coefficient_index[self.scan_plane][3]] * 10)
    
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
        self.abs_3d.set_title('Absolute Magnitude')
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
        self.plot_323.set_title('$\int$By')
        self.plot_324 = self.fig_p2.add_subplot(324)
        self.plot_324.set_title('$\int$Bx')
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
        self.plot_323.set_xlabel(f'{self.plot_axis} axis [cm]')
        self.plot_323.set_ylabel('By [G$\cdot$cm]')
        self.plot_323.grid()
        
    def generate_2d_plot_324(self):
        self.plot_324.plot(self.scan_integrals[:, 0], self.scan_integrals[:, self.integrals_index['Bx']], marker='.', label='Bx Integrals')
        self.plot_324.set_xlabel(f'{self.plot_axis} axis [cm]')
        self.plot_324.set_ylabel('Bx [G$\cdot$cm]')
        self.plot_324.grid()
    
    def generate_table(self):
        # Plot table of self.all_coeffs
        units = ['G', 'G/cm', 'G/$cm^2$', 'G/$cm^3$', 'G/$cm^4$', 'G/$cm^5$', 'G/$cm^6$', 'G/$cm^7$', 'G/$cm^8$', 'G/$cm^9$']
        int_units = ['$G \cdot cm$', 'G', 'G/cm', 'G/$cm^2$', 'G/$cm^3$', 'G/$cm^4$', 'G/$cm^5$', 'G/$cm^6$', 'G/$cm^7$', 'G/$cm^8$']
        str_coeffs = self.all_coeffs.round(1).astype(str)
        str_coeffs = np.insert(str_coeffs, 2, units, axis=1)
        str_coeffs = np.insert(str_coeffs, 5, int_units, axis=1)
        str_coeffs_header = self.coeffs_header.copy()
        str_coeffs_header.insert(2, 'Units')
        str_coeffs_header.insert(5, 'Units')
        # t = self.coeffs_table.table(cellText=self.all_coeffs, colLabels=self.coeffs_header, rowLabels=[1,2,3,4,5,6,7,8,9,10], loc='center')
        t = self.coeffs_table.table(cellText=str_coeffs, colLabels=str_coeffs_header, rowLabels=[1,2,3,4,5,6,7,8,9,10], loc='center', colWidths=[0.2, 0.25, 0.15, 0.2, 0.25, 0.15])
        t.auto_set_font_size(False)
        t.set_fontsize(12)
        t.scale(1, 1.3)

    def generate_text_info(self):
        # Generate text information
        if self.scan_plane == 'zx':
            info = '\n'.join((f'Integrated Quadrupole Strength: {self.integrated_magnetic_value:.1f} G',
                            f'Quadrupole Magnetic Length: {self.quadrupole_magnetic_length:.3f} cm',
                            f'Dipole Magnetic Length: {self.dipole_magnetic_length:.3f} cm',
                            f'Offset: $\Delta$x: {self.offset[0]:.3f} mm $\Delta$y: {self.offset[1]:.3f} mm'))
        elif self.scan_plane == 'yz':
            info = '\n'.join((f'Integrated Quadrupole Strength: {self.integrated_magnetic_value:.1f} G',
                            f'Quadrupole Magnetic Length: {self.quadrupole_magnetic_length:.3f} cm',
                            f'Offset: $\Delta$x: {self.offset[1]:.3f} mm $\Delta$y: {self.offset[0]:.3f} mm'))
        
        self.fig_p2.text(0.6, 0.25, info, verticalalignment='top', bbox=self.bbox_props)

    def show_plots(self):
        plt.show()

class DipolePlotDashboard:
    def __init__(self, data, filepath):
        self.data = data
        self.filepath = filepath
        self.process_data()
        self.create_plots()
    
    def process_data(self):
        self.hp_interp, self.xyzB_grid, self.x_mesh, self.z_mesh, self.B_grid = bc.interpolate_grid(self.data)

    def create_plots(self):
        print(f'filepath: {self.filepath}')
        bc.plot_field_map(self.x_mesh, self.z_mesh, self.B_grid,
                          save_file=self.filepath + '/Figure 1 colormap.pdf', show_plot=False)
        

if __name__ == '__main__':
    root = tk.Tk()
    pw = PlotWindow(root)
    root.mainloop()