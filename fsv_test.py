import numpy as np
import matplotlib.pyplot as plt
from calibration import filter_data

x_pos = np.genfromtxt('fsv_x_pos.txt')
x_neg = np.genfromtxt('fsv_x_neg.txt')
y_pos = np.genfromtxt('fsv_y_pos.txt')
y_neg = np.genfromtxt('fsv_y_neg.txt')
z_pos = np.genfromtxt('fsv_z_pos.txt')
z_neg = np.genfromtxt('fsv_z_neg.txt')

filt_cutoff = 500
fit_lc = 175

x_pos_filt = filter_data(x_pos[:, 3], filt_cutoff)
x_neg_filt = filter_data(x_neg[:, 3], filt_cutoff)
y_pos_filt = filter_data(y_pos[:, 3], filt_cutoff)
y_neg_filt = filter_data(y_neg[:, 3], filt_cutoff)
z_pos_filt = filter_data(z_pos[:, 1], filt_cutoff)
z_neg_filt = filter_data(z_neg[:, 1], filt_cutoff)

xp_lc = x_pos_filt[filt_cutoff:-filt_cutoff]
xnp_lc = x_neg_filt[filt_cutoff:-filt_cutoff]
yp_lc = y_pos_filt[filt_cutoff:-filt_cutoff]
yn_lc = y_neg_filt[filt_cutoff:-filt_cutoff]
zp_lc = z_pos_filt[filt_cutoff:-filt_cutoff]
zn_lc = z_neg_filt[filt_cutoff:-filt_cutoff]
f_slice = slice(filt_cutoff, -filt_cutoff)

fig, ax = plt.subplots(nrows=3, ncols=1)
ax[0].plot(x_pos[:, 0], x_pos[:, 3], label='x_pos')
ax[0].plot(x_neg[:, 0], x_neg[:, 3], label='x_neg')
ax[1].plot(y_pos[:, 0], y_pos[:, 3], label='y_pos')
ax[1].plot(y_neg[:, 0], y_neg[:, 3], label='y_neg')
ax[2].plot(z_pos[:, 0], z_pos[:, 1], label='z_pos')
ax[2].plot(z_neg[:, 0], z_neg[:, 1], label='z_neg')
ax[0].set_title('FSV X')
ax[1].set_title('FSV Y')
ax[2].set_title('FSV Z')
for i in range(3):
    ax[i].grid()
    ax[i].legend()
plt.tight_layout()

fig2, ax2 = plt.subplots(nrows=3, ncols=1)
ax2[0].plot(x_pos[:, 0][filt_cutoff:-filt_cutoff], x_pos_filt[filt_cutoff:-filt_cutoff], label='x_pos filt')
ax2[0].plot(x_neg[:, 0][filt_cutoff:-filt_cutoff], x_neg_filt[filt_cutoff:-filt_cutoff], label='x_neg filt')
ax2[1].plot(y_pos[:, 0][filt_cutoff:-filt_cutoff], y_pos_filt[filt_cutoff:-filt_cutoff], label='y_pos filt')
ax2[1].plot(y_neg[:, 0][filt_cutoff:-filt_cutoff], y_neg_filt[filt_cutoff:-filt_cutoff], label='y_neg filt')
ax2[2].plot(z_pos[:, 0][filt_cutoff:-filt_cutoff], z_pos_filt[filt_cutoff:-filt_cutoff], label='z_pos filt')
ax2[2].plot(z_neg[:, 0][filt_cutoff:-filt_cutoff], z_neg_filt[filt_cutoff:-filt_cutoff], label='z_neg filt')
for i in range(3):
    ax2[i].grid()
    ax2[i].legend()
plt.tight_layout()


xp_min_index = np.where(xp_lc == xp_lc.min())[0][0] + filt_cutoff + fit_lc
xp_max_index = np.where(xp_lc == xp_lc.max())[0][0] + filt_cutoff - fit_lc

xp_pf = np.polyfit(x_pos[:, 0][xp_max_index:xp_min_index], x_pos_filt[xp_max_index:xp_min_index], 3)

fig3, ax3 = plt.subplots()
ax3.plot(x_pos[:, 0][xp_max_index:xp_min_index], x_pos_filt[xp_max_index:xp_min_index])
ax3.plot(x_pos[:, 0][xp_max_index:xp_min_index], np.polyval(xp_pf, x_pos[:, 0][xp_max_index:xp_min_index]), linestyle='dashed', label='fit')
ax3.grid()

print(f'x_pos shape: {x_pos.shape}')
print(f'xp_min_index: {xp_min_index}')
print(f'xp_max_index: {xp_max_index}')

plt.tight_layout()
plt.show()