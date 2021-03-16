import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from zeisscmm import transform_points

data = np.genfromtxt('scan_data.txt', delimiter=' ', skip_header=1)
data = data[:, :-1]
coord_diff = np.genfromtxt('test_program/mag_test_mcs.txt', delimiter=' ')
R = coord_diff[:9].reshape((3,3))
T = coord_diff[9:]
data[:, :3] = transform_points(data[:, :3], T, R, inverse=True)
x = data[:, 0]
y = data[:, 1]
z = data[:, 2]
Bx = data[:, 3]
By = data[:, 4]
Bz = data[:, 5]
# print(np.array((Bx, By, Bz)).T.shape)
B_norm = np.linalg.norm(np.array((Bx, By, Bz)).T, axis=1)
B_norm_cmap = B_norm/B_norm.max()
# print('B norm:\n', B_norm[:10])
Bx_hat = Bx/B_norm
By_hat = By/B_norm
Bz_hat = Bz/B_norm
# print('Bx_hat:\n', Bx_hat[:10])

data_pcs = np.array([x, y, z, Bx_hat, By_hat, Bz_hat]).T
data_pcs = data_pcs[(data_pcs[:, 0] > -5.) & (data_pcs[:, 0] < 25.)]
# print(data_pcs.shape)

start = 0
end = -1

# print(data_pcs[start:end])
'''
fig = plt.figure(figsize=(16,8))
ax = fig.gca(projection='3d')
q = ax.quiver(x[start:end], y[start:end], z[start:end],
              Bx_hat[start:end], By_hat[start:end], Bz_hat[start:end],
              length=0.005)
'''
cmap = plt.get_cmap(name='rainbow')
fig2 = plt.figure(figsize=(11,8.5))
ax2 = fig2.gca(projection='3d', proj_type='ortho', azim=-45., elev=5.)
q2 = ax2.quiver(data_pcs[start:end, 0], data_pcs[start:end, 1], data_pcs[start:end, 2],
                data_pcs[start:end, 3], data_pcs[start:end, 4], data_pcs[start:end, 5],
                color=cmap(B_norm_cmap[start:end]), cmap=cmap, length=0.5, normalize=False)
fig2.colorbar(q2)
ax2.set_xlabel('x axis [mm]')
ax2.set_ylabel('y axis [mm]')
ax2.set_zlabel('z axis [mm]')
ax2.set_xlim(-5, 25)
ax2.set_ylim(6, 69)
ax2.set_zlim(116, 120)

plt.show()
