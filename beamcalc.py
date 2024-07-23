import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import RBFInterpolator
from scipy.integrate import simps

def interpolate_grid(filename, ds=0.0005):
    '''
    Read hall probe data from file, create a uniform grid,
    and generate interpolated field values on the grid.
    Input:  filename (file path to hall probe data)
            ds step (in meters)
    Output: (interpolation object, grid data, x mesh, z mesh, B field grid)
    '''
    xyzB = np.genfromtxt(filename)
    xyzB /= 1000 # convert to SI units (m and T)
    hp_interp = RBFInterpolator(xyzB[:, :3], xyzB[:, 3:], kernel='thin_plate_spline')
    xyz_min = np.min(xyzB[:, :3], axis=0)
    xyz_max = np.max(xyzB[:, :3], axis=0)
    x = np.arange(xyz_min[0], xyz_max[0], ds)
    z = np.arange(xyz_min[2], xyz_max[2], ds)
    xyzB_grid = np.zeros((len(z)*len(x), 6))
    for i, x_value in enumerate(x):
        for j, z_value in enumerate(z):
            xyzB_grid[i*len(z) + j] = [x_value, 0, z_value, 0, 0, 0]
    xyzB_grid[:, 3:] = hp_interp(xyzB_grid[:, :3])
    x_mesh, z_mesh = np.meshgrid(x, z)
    Bx = np.zeros_like(x_mesh)
    By = np.zeros_like(x_mesh)
    Bz = np.zeros_like(x_mesh)
    for i in range(xyzB_grid.shape[0]):
        xi = np.where(x == xyzB_grid[i, 0])[0]
        zi = np.where(z == xyzB_grid[i, 2])[0]
        Bx[zi, xi] = xyzB_grid[i, 3]
        By[zi, xi] = xyzB_grid[i, 4]
        Bz[zi, xi] = xyzB_grid[i, 5]
    B_grid = np.stack((Bx, By, Bz), axis=-1)
    return (hp_interp, xyzB_grid, x_mesh, z_mesh, B_grid)

def plot_field_map(x_mesh, z_mesh, B, save_file=None, show_plot=True):
    '''
    Takes meshgrid and interpolated field data and plots the field map.
    '''
    fig, ax = plt.subplots(3, 1, figsize=(11, 8.5))
    titles = ['$B_x$ [T]', '$B_y$ [T]', '$B_z$ [T]']
    for i in range(3):
        # ax[i].contourf(z_mesh, x_mesh, B[:, :, i], levels=30, cmap='viridis')
        contour = ax[i].contourf(z_mesh, x_mesh, B[:, :, i], levels=30, cmap='viridis')
        cbar = fig.colorbar(contour, ax=ax[i])
        cbar.set_label(titles[i])
        ax[i].set_title(titles[i])
        ax[i].set_xlabel('z [m]')
        ax[i].set_ylabel('x [m]')
    plt.tight_layout()
    if save_file:
        plt.savefig(save_file, format='pdf', dpi=300)
    if show_plot:
        plt.show()

def beam_traj(hp_interp, xyzB, xb, xb_prime, yb, yb_prime, zb, zb_max, ds, hr):
    '''
    Calculate beam trajectory given initial conditions and field map.
    Inputs: hp_interp - RBFInterpolator object
            xyzB - grid data - not currently used.  future use for domain verification
            xb - initial x position
            xb_prime - initial x angle
            yb - initial y position
            yb_prime - initial y angle
            zb - initial z position
            zb_max - final z position
            ds - step size
            hr - beam stiffness
    Output: xyzB_traj - xyz and B field values along trajectory
            xy_prime - x and y angles along trajectory
    '''
    z = np.arange(zb, zb_max, ds)
    xp = np.zeros(len(z))
    yp = np.zeros(len(z))
    xyzB_traj = np.zeros((len(z), 6))
    xyzB_traj[0] = [xb, yb, zb, 0, 0, 0]
    xyzB_traj[:, 2] = z
    xp[0] = xb_prime
    yp[0] = yb_prime
    for i, z_step in enumerate(xyzB_traj):
        xyzB_traj[i, 3:] = hp_interp(z_step[:3].reshape((1,3)))
        if i < len(z) - 1:
            xyzB_traj[i+1, 0] = xyzB_traj[i, 0] + ds * xp[i]
            xyzB_traj[i+1, 1] = xyzB_traj[i, 1] + ds * yp[i]
            dxb_prime = ds * xyzB_traj[i, 4] / hr
            xp[i+1] = xp[i] + dxb_prime
            dyb_prime = ds * xyzB_traj[i, 3] / hr
            yp[i+1] = yp[i] + dyb_prime
    xy_prime = np.stack((xp, yp), axis=-1)
    return xyzB_traj, xy_prime

def plot_trajectory(xyzB_traj, xy_prime, save_file=None, show_plot=True):
    '''
    Plot beam trajectory and angles.
    If xyzB_traj and xy_prime are 3-dimensional arrays,
    plot multiple trajectories.
    '''
    fig, ax = plt.subplots(3, 1, figsize=(11, 8.5), sharex=True)
    ylabels = ['x-prime [rad]', 'x-axis [m]', '$B_y$ [T]']

    if xyzB_traj.ndim == 3 and xy_prime.ndim == 3:
        for i, traj in enumerate(xyzB_traj):
            ax[0].plot(traj[:, 2], xy_prime[i][:, 0])
            ax[1].plot(traj[:, 2], traj[:, 0])
            ax[2].plot(traj[:, 2], traj[:, 4])
        ax[0].set_xlabel('z-axis [m]')
        ax[0].set_ylabel(ylabels[0])
        ax[0].grid()
        ax[1].set_ylabel(ylabels[1])
        ax[1].grid()
        ax[2].set_xlabel('z-axis [m]')
        ax[2].set_ylabel(ylabels[2])
        ax[2].grid()
        plt.tight_layout()

    else:
        ax[0].plot(xyzB_traj[:, 2], xy_prime[:, 0])
        ax[1].plot(xyzB_traj[:, 2], xyzB_traj[:, 0])
        ax[2].plot(xyzB_traj[:, 2], xyzB_traj[:, 4])
        ax[2].set_xlabel('z-axis [m]')
        for i in range(3):
            ax[i].set_ylabel(ylabels[i])
            ax[i].grid()
        plt.tight_layout()
    if save_file:
        plt.savefig(save_file, format='pdf', dpi=300)
    if show_plot:
        plt.show()

def __plot_traj_diff__(start_positions, dtetas, fit_dteta, xc, save_file=None, show_plot=True):
    fig, ax = plt.subplots(figsize=(11, 8.5))
    ax.scatter(start_positions, dtetas[:, 0], marker='o', label='data')
    ax.plot(start_positions, np.polyval(fit_dteta, start_positions), 'r--', label='fit')
    ax.scatter(xc, np.polyval(fit_dteta, xc), marker='x', color='black', label=f'xc={xc:.6f}')
    ax.set_xlabel('x-axis [m]')
    ax.set_ylabel('$Teta_{out} - Teta_{in}$ [rad]')
    ax.grid()
    ax.legend()
    plt.tight_layout()
    if save_file:
        plt.savefig(save_file, format='pdf', dpi=300)
    if show_plot:
        plt.show()

def find_optimal_start(hp_data_interp, xyzB_grid, Teta_in, x_min, x_max, ds, HR, save_plot=False, show_plot=True):
    trajectories = []
    xy_primes = []
    start_positions = np.arange(x_min, x_max + ds, ds)
    print(f'start_positions shape = {start_positions.shape}')
    for start in start_positions:
        traj, xy_prime = beam_traj(hp_data_interp, xyzB_grid, start, Teta_in, 0, 0, -.246, .246, ds, HR)
        trajectories.append(traj)
        xy_primes.append(xy_prime)
    trajectories = np.array(trajectories)
    xy_primes = np.array(xy_primes)
    dtetas = xy_primes[:, 0] + xy_primes[:, -1]
    print(f'dtetas shape = {dtetas[:, 0].shape}')
    fit_dteta = np.polyfit(start_positions, dtetas[:, 0], 1)
    xc = np.roots(fit_dteta)[0]
    opt_traj, opt_xy_prime = beam_traj(hp_data_interp, xyzB_grid, xc, Teta_in, 0, 0, -.246, .246, ds, HR)
    if save_plot:
        plot_trajectory(trajectories, xy_primes, save_file='trajectories.pdf', show_plot=False)
        plot_trajectory(opt_traj, opt_xy_prime, save_file='optimal_trajectory.pdf', show_plot=False)
        __plot_traj_diff__(start_positions, dtetas, fit_dteta, xc)
    if show_plot:
        plot_trajectory(trajectories, xy_primes)
        plot_trajectory(opt_traj, opt_xy_prime)
        __plot_traj_diff__(start_positions, dtetas, fit_dteta, xc)
        plt.show()
    return opt_traj, opt_xy_prime, xc

def field_on_traj(optimal_traj, opt_xy_prime, hp_interp, delta=0.0005):
    dx = np.arange(-0.010, 0.010 + delta, delta)
    yh = np.zeros_like(dx)
    B_all = np.zeros((optimal_traj.shape[0], dx.shape[0],3))
    b_pf = np.zeros((optimal_traj.shape[0], 6))
    a_pf = np.zeros_like(b_pf)
    for i, z_step in enumerate(optimal_traj):
        xh = z_step[0] + dx * np.cos(opt_xy_prime[i][0])
        zh = z_step[2] - dx * np.sin(opt_xy_prime[i][0])
        B_all[i] = hp_interp(np.stack((xh, yh, zh), axis=-1))
    for j, B_dx in enumerate(B_all):
        b_pf[j] = np.polyfit(dx, B_dx[:, 1], 5)
        a_pf[j] = np.polyfit(dx, B_dx[:, 0], 5)
    int_b_pf = simps(b_pf, dx=delta, axis=0)
    int_a_pf = simps(a_pf, dx=delta, axis=0)
    return b_pf, a_pf, int_b_pf, int_a_pf

def plot_coeffs(z, b_coeffs, a_coeffs, int_b_coeffs, int_a_coeffs, save_file=None, show_plot=True):
    fig1, ax1 = plt.subplots(nrows=2, ncols=1, figsize=(11, 8.5), sharex=True)
    ax1[0].set_title(f'$\\int B1 =$ {int_b_coeffs[-1]:.5f} $T \\cdot m$ ; $\\int A1 =$ {int_a_coeffs[-1]:.5f} $T \\cdot m$')
    ax1[1].set_title(f'$\\int B2 =$ {int_b_coeffs[-2]:.5f} ; $\\int A2 =$ {int_a_coeffs[-2]:.5f}')
    ax1[0].plot(z, b_coeffs[:, -1], label='$B_y$ [B1]')
    ax1[0].plot(z, a_coeffs[:, -1] * 100, label='$B_x$*100 [A1]')
    ax1[1].plot(z, b_coeffs[:, -2], label='$\\frac{\\delta B_y}{\\delta x}$ [B2]')
    ax1[1].plot(z, a_coeffs[:, -2] * 100, label='$\\frac{\\delta B_x}{\\delta x}$*100 [A2]')
    ax1[0].set_ylabel('T')
    ax1[1].set_xlabel('z-axis [m]')
    ax1[1].set_ylabel('T/m')
    ax1[0].legend()
    ax1[1].legend()
    ax1[0].grid()
    ax1[1].grid()
    plt.tight_layout()

    fig2, ax2 = plt.subplots(nrows=2, ncols=1, figsize=(11, 8.5), sharex=True)
    ax2[0].set_title(f'$\\int B3 =$ {int_b_coeffs[-3]:.5f} $T \\cdot m / m^2$ ; $\\int A3 =$ {int_a_coeffs[-3]:.5f} $T \\cdot m / m^2$')
    ax2[1].set_title(f'$\\int B4 =$ {int_b_coeffs[-4]:.5f} $T \\cdot m / m^3$ ; $\\int A4 =$ {int_a_coeffs[-4]:.5f} $T \\cdot m / m^3$')
    ax2[0].plot(z, b_coeffs[:, -3], label='B3')
    ax2[0].plot(z, a_coeffs[:, -3], label='A3')
    ax2[1].plot(z, b_coeffs[:, -4], label='B4')
    ax2[1].plot(z, a_coeffs[:, -4], label='A4')
    ax2[0].set_ylabel('$T/m^2$')
    ax2[1].set_xlabel('z-axis [m]')
    ax2[1].set_ylabel('$T/m^3$')
    ax2[0].grid()
    ax2[1].grid()
    ax2[0].legend()
    ax2[1].legend()
    plt.tight_layout()

    fig3, ax3 = plt.subplots(nrows=2, ncols=1, figsize=(11, 8.5), sharex=True)
    ax3[0].set_title(f'$\\int B5 =$ {int_b_coeffs[-5]:.5f} $T \\cdot m / m^4$ ; $\\int A5 =$ {int_a_coeffs[-5]:.5f} $T \\cdot m / m^4$')
    ax3[1].set_title(f'$\\int B6 =$ {int_b_coeffs[-6]:.5f} $T \\cdot m / m^5$ ; $\\int A6 =$ {int_a_coeffs[-6]:.5f} $T \\cdot m / m^5$')
    ax3[0].plot(z, b_coeffs[:, -5], label='B5')
    ax3[0].plot(z, a_coeffs[:, -5], label='A5')
    ax3[1].plot(z, b_coeffs[:, -6], label='B6')
    ax3[1].plot(z, a_coeffs[:, -6], label='A6')
    ax3[0].set_ylabel('$T/m^4$')
    ax3[1].set_xlabel('z-axis [m]')
    ax3[1].set_ylabel('$T/m^5$')
    ax3[0].grid()
    ax3[1].grid()
    ax3[0].legend()
    ax3[1].legend()
    plt.tight_layout()
    if save_file:
        fig1.savefig(save_file + '_1.pdf', format='pdf', dpi=300)
        fig2.savefig(save_file + '_2.pdf', format='pdf', dpi=300)
        fig3.savefig(save_file + '_3.pdf', format='pdf', dpi=300)
    if show_plot:
        plt.show()

if __name__ == '__main__':
    pass