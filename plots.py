import numpy as np
from scipy.integrate import quad
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pickle

class PlotDashboard:
    plane_index = {'xy': (0, 1, 'x axis [mm]', 'y axis[mm]'),
                   'yz': (1, 2, 'y axis [mm]', 'z axis [mm]'),
                   'zx': (2, 0, 'z axis [mm]', 'x axis [mm]')}
    int_across_index = {'x': 0, 'y': 1, 'z': 2}
    def __init__(self):
        # self.generate_header()
        pass

    def create_figs(self):
        self.fig_p1 = plt.figure(figsize=(11, 8.5))
        self.fig_p2 = plt.figure(figsize=(11, 8.5))
        self.fig_single_line = plt.figure(figsize=(8.5, 11))
        self.fig_p2.subplots_adjust(hspace=0.3)
        self.fig_p1.suptitle('3D Plots')
        self.fig_p2.suptitle('2D Plots')
        self.fig_single_line.suptitle('Single line scan')
        # Place text boxes containing header information
        # self.fig_p1.text(0.03, 0.97, f'Magnet: {self.header[0]}-{self.header[1]}\nCurrent: {self.header[2]}', verticalalignment='top', bbox=self.bbox_props)
        # self.fig_p2.text(0.03, 0.97, f'Magnet: {self.header[0]}-{self.header[1]}\nCurrent: {self.header[2]}', verticalalignment='top', bbox=self.bbox_props)
        # self.fig_single_line.text(0.03, 0.97, f'Magnet: {self.header[0]}-{self.header[1]}\nCurrent: {self.header[2]}', verticalalignment='top', bbox=self.bbox_props)
    
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
        # self.x_by_mTmm = self.fig_p2.add_subplot(131)
        # self.x_by_mTmm.set_title(r'$\int_{-15}^{15} B_y(x)\mathrm{d}x$')
        # self.x_by_mTmm.set_xlabel(self.plane_index[plane][3])
        # self.x_by_mTmm.set_xlabel('dx [mm]')
        # self.x_by_mTmm.set_ylabel('mT$\cdot$mm')
        self.x_bx = self.fig_p2.add_subplot(131)
        self.x_bx.set_title('Bx')
        self.x_bx.set_xlabel(self.plane_index[self.plane][3])
        self.x_bx.set_ylabel('Bx [mT]')
        self.x_by = self.fig_p2.add_subplot(132)
        self.x_by.set_title('By')
        self.x_by.set_xlabel(self.plane_index[self.plane][3])
        self.x_by.set_ylabel('By [mT]')
        self.x_bz = self.fig_p2.add_subplot(133)
        self.x_bz.set_title('Bz')
        self.x_bz.set_xlabel(self.plane_index[self.plane][3])
        self.x_bz.set_ylabel('Bz [mT]')
        # 2D Single line plot
        self.line_bx = self.fig_single_line.add_subplot(311)
        self.line_bx.set_title('Bx')
        self.line_by = self.fig_single_line.add_subplot(312)
        self.line_by.set_title('By')
        self.line_bz = self.fig_single_line.add_subplot(313)
        self.line_bz.set_title('Bz')
    
    def generate_header(self):
        # header pickle file is a list [magnet, serial number, current, notes]
        self.header = pickle.load('magnet_info.pkl')
        self.bbox_props = dict(boxstyle='round', facecolor='grey', alpha=0.3)
    
    def plot_area_data(self, data, plane, integrate_across='x', from_to=(-15, 15), where=('z', 0), scan_interval=1):
        '''
        Options for kwargs:
            integrate_across: str 'x', 'y', 'z'
            from_to: tuple (-15, 15)
            where: tuple ('z', 0) or ('y', 0) or ('x', 0)
        '''
        self.data_3d = data
        self.data_2d = data[(data[:, self.int_across_index[integrate_across]] > where[1]-scan_interval/2) & (data[:, self.int_across_index[integrate_across]] < where[1]+scan_interval/2)]
        self.plane = plane
        self.integrate_across = integrate_across
        self.from_to = from_to
        self.where = where
        self.fit_2d()
        self.create_figs()
        self.create_subplots()
        self.plot_3d_abs()
        self.plot_3d_bx()
        self.plot_3d_by()
        self.plot_3d_bz()
        # self.plot_2d_x_by_mTmm()
        self.plot_2d_x_bx()
        self.plot_2d_x_by()
        self.plot_2d_x_bz()
        # Save figures as pdf
        self.fig_p1.savefig('3d_plots.pdf', bbox_inches='tight')
        self.fig_p2.savefig('2d_plots.pdf', bbox_inches='tight')

    def plot_3d_abs(self):
        Bxyz_abs = np.linalg.norm(self.data_3d[:, 3:], axis=1)
        # Plot 3d Absolute values
        self.abs_3d.scatter(self.data_3d[:, self.plane_index[self.plane][0]], self.data_3d[:, self.plane_index[self.plane][1]], Bxyz_abs,
                            marker='.', cmap='rainbow', c=Bxyz_abs)
        # Add colorbar
        self.fig_p1.colorbar(self.abs_3d.collections[0], ax=self.abs_3d, pad=0.2)
    
    def plot_3d_bx(self):
        # Plot 3d Bx
        self.bx_3d.scatter(self.data_3d[:, self.plane_index[self.plane][0]], self.data_3d[:, self.plane_index[self.plane][1]], self.data_3d[:, 3],
                           marker='.', cmap='rainbow', c=data[:, 3])
        # Add colorbar
        self.fig_p1.colorbar(self.bx_3d.collections[0], ax=self.bx_3d, pad=0.2)
    
    def plot_3d_by(self):
        # Plot 3d By
        self.by_3d.scatter(self.data_3d[:, self.plane_index[self.plane][0]], self.data_3d[:, self.plane_index[self.plane][1]], self.data_3d[:, 4],
                           marker='.', cmap='rainbow', c=data[:, 4])
        # Add colorbar
        self.fig_p1.colorbar(self.by_3d.collections[0], ax=self.by_3d, pad=0.2)
    
    def plot_3d_bz(self):
        # Plot 3d Bz
        self.bz_3d.scatter(self.data_3d[:, self.plane_index[self.plane][0]], self.data_3d[:, self.plane_index[self.plane][1]], self.data_3d[:, 5],
                           marker='.', cmap='rainbow', c=data[:, 5])
        # Add colorbar
        self.fig_p1.colorbar(self.bz_3d.collections[0], ax=self.bz_3d, pad=0.2)
    
    def fit_2d(self):
        fit_func = lambda x, c: c[0] * x + c[1]
        self.bx_fit_coeffs = np.polyfit(self.data_2d[:, self.int_across_index[self.integrate_across]], self.data_2d[:, 3], 1)
        self.by_fit_coeffs = np.polyfit(self.data_2d[:, self.int_across_index[self.integrate_across]], self.data_2d[:, 4], 1)
        self.bz_fit_coeffs = np.polyfit(self.data_2d[:, self.int_across_index[self.integrate_across]], self.data_2d[:, 5], 1)
        self.int_x_axis = np.linspace(self.from_to[0], self.from_to[1], len(self.data_2d[:, self.int_across_index[self.integrate_across]]))
        self.bx_fit_y_axis = fit_func(self.int_x_axis, self.bx_fit_coeffs)
        self.by_fit_y_axis = fit_func(self.int_x_axis, self.by_fit_coeffs)
        self.bz_fit_y_axis = fit_func(self.int_x_axis, self.bz_fit_coeffs)
        self.bx_integral = quad(fit_func, self.from_to[0], self.from_to[1], args=self.bx_fit_coeffs)[0]
        self.by_integral = quad(fit_func, self.from_to[0], self.from_to[1], args=self.by_fit_coeffs)[0]
        self.bz_integral = quad(fit_func, self.from_to[0], self.from_to[1], args=self.bz_fit_coeffs)[0]

    def plot_2d_x_bx(self):
        # Plot 2d Bx
        self.x_bx.scatter(self.data_2d[:, self.plane_index[self.plane][1]], self.data_2d[:, 3], marker='.', label='Measured data')
        # plot fit
        self.x_bx.plot(self.int_x_axis, self.bx_fit_y_axis,
                       color='red', linestyle='dashed', label=f'Fit: {self.bx_fit_coeffs[0]:.3f}x {self.bx_fit_coeffs[1]:+.3f}')
        # fill between fit and x axis
        self.x_bx.fill_between(self.int_x_axis, self.bx_fit_y_axis, alpha=0.2, color='green', label=f'Integral: {self.bx_integral:.3f} mT$\cdot$mm')
        self.x_bx.grid()
        self.x_bx.legend()
    
    def plot_2d_x_by(self):
        # Plot 2d By
        self.x_by.scatter(self.data_2d[:, self.plane_index[self.plane][1]], self.data_2d[:, 4], marker='.', label='Measured data')
        # plot fit
        self.x_by.plot(self.int_x_axis, self.by_fit_y_axis, color='red', linestyle='dashed', label=f'Fit: {self.by_fit_coeffs[0]:.3f}x {self.by_fit_coeffs[1]:+.3f}')
        # fill between fit and x axis
        self.x_by.fill_between(self.int_x_axis, self.by_fit_y_axis, alpha=0.2, color='green', label=f'Integral: {self.by_integral:.3f} mT$\cdot$mm')
        self.x_by.grid()
        self.x_by.legend()
    
    def plot_2d_x_bz(self):
        # Plot 2d Bz
        self.x_bz.scatter(self.data_2d[:, self.plane_index[self.plane][1]], self.data_2d[:, 5], marker='.', label='Bz')
        # plot fit
        self.x_bz.plot(self.int_x_axis, self.bz_fit_y_axis,
                       color='red', linestyle='dashed', label=f'Fit: {self.bz_fit_coeffs[0]:.3f}x {self.bz_fit_coeffs[1]:+.3f}')
        # fill between fit and x axis
        self.x_bz.fill_between(self.int_x_axis, self.bz_fit_y_axis, alpha=0.2, color='green', label=f'Integral: {self.bz_integral:.3f} mT$\cdot$mm')
        self.x_bz.grid()
        self.x_bz.legend()
    
    def plot_single_line(self, data, plot_axis='x', integrate_across=(-15, 15), fit=1):
        plot_axis_index = {'x': 0, 'y': 1, 'z': 2}
        fit_funcs = {1: lambda x, c: c[0] * x + c[1],
                     2: lambda x, c: c[0] * x ** 2 + c[1] * x + c[2],
                     3: lambda x, c: c[0] * x ** 3 + c[1] * x ** 2 + c[2] * x + c[3]}
        x_values = np.linspace(integrate_across[0], integrate_across[1], 100)
        bx_fit_coeffs = np.polyfit(data[:, plot_axis_index[plot_axis]], data[:, 3], fit)
        by_fit_coeffs = np.polyfit(data[:, plot_axis_index[plot_axis]], data[:, 4], fit)
        bz_fit_coeffs = np.polyfit(data[:, plot_axis_index[plot_axis]], data[:, 5], fit)
        bx_integral = quad(fit_funcs[fit], integrate_across[0], integrate_across[1], args=bx_fit_coeffs)[0]
        by_integral = quad(fit_funcs[fit], integrate_across[0], integrate_across[1], args=by_fit_coeffs)[0]
        bz_integral = quad(fit_funcs[fit], integrate_across[0], integrate_across[1], args=bz_fit_coeffs)[0]
        integrals = [bx_integral, by_integral, bz_integral]
        axs = [self.line_bx, self.line_by, self.line_bz]
        fits = [bx_fit_coeffs, by_fit_coeffs, bz_fit_coeffs]
        self.line_bx.scatter(data[:, plot_axis_index[plot_axis]], data[:, 3], marker='.', label='Bx')
        self.line_by.scatter(data[:, plot_axis_index[plot_axis]], data[:, 4], marker='.', label='By')
        self.line_bz.scatter(data[:, plot_axis_index[plot_axis]], data[:, 5], marker='.', label='Bz')
        for i, p in enumerate(axs):
            if fit == 1:
                p.plot(x_values, np.polyval(fits[i], x_values), color='red', linestyle='dashed', label=f'Fit: {fits[i][0]:.3f}x {fits[i][1]:+.3f}')
                p.fill_between(x_values, np.polyval(fits[i], x_values), alpha=0.2, color='green', label=f'Integral: {integrals[i]} mT$\cdot$mm')
            elif fit == 2:
                p.plot(x_values, np.polyval(fits[i], x_values), color='red', linestyle='dashed', label=f'Fit: {fits[i][0]:.3f}$x^2$ {fits[i][1]:+.3f}x {fits[i][2]:+.3f}')
                p.fill_between(x_values, np.polyval(fits[i], x_values), alpha=0.2, color='green', label=f'Integral: {integrals[i]} mT$\cdot$mm')
            elif fit == 3:
                p.plot(x_values, np.polyval(fits[i], x_values), color='red', linestyle='dashed', label=f'Fit: {fits[i][0]:.3f}$x^3$ {fits[i][1]:+.3f}$x^2$ {fits[i][2]:+.3f}x {fits[i][3]:+.3f}')
                p.fill_between(x_values, np.polyval(fits[i], x_values), alpha=0.2, color='green', label=f'Integral: {integrals[i]} mT$\cdot$mm')
        for p in axs:
            p.xlabel(f'{plot_axis} axis [mm]')
            p.ylabel('B [mT]')
            p.grid()
            p.legend()
        # Save plots as pdf
        self.fig_single_line.savefig(f'./scans/{self.header[0]}-{self.header[1]}/{self.header[0]}-{self.header[1]} Single Line Scan.pdf')

    def show_plots(self):
        plt.show()

if __name__ == '__main__':
    data = np.genfromtxt('area 2023-04-19.txt')
    plot = PlotDashboard()
    plot.plot_area_data(data, plane='zx', integrate_across='z', from_to=(-50, 50), where=('x', 0), scan_interval=1)
    plot.show_plots()