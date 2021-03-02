from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np

mcs = np.genfromtxt('mcs.txt', delimiter=';')

e1 = np.deg2rad(mcs[3])
e2 = np.deg2rad(mcs[4])
e4 = np.deg2rad(mcs[5])
trans_xyz = mcs[:3]

Rz_e1 = np.array([[np.cos(e1), -np.sin(e1), 0],
                  [np.sin(e1), np.cos(e1), 0],
                  [0, 0, 1]])
Rx_e2 = np.array([[1, 0, 0],
                  [0, np.cos(e2), -np.sin(e2)],
                  [0, np.sin(e2), np.cos(e2)]])
Rz_e4 = np.array([[np.cos(e4), -np.sin(e4), 0],
                  [np.sin(e4), np.cos(e4), 0],
                  [0, 0, 1]])
R = Rz_e1@Rx_e2@Rz_e4

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.set_xlabel('x axis')
ax.set_ylabel('y axis')
ax.set_zlabel('z axis')
ax.plot([0, 1], [0, 0], [0, 0], color='C0', ls='-')
ax.plot([0, 0], [0, 1], [0, 0], color='C0', ls='--')
ax.plot([0, 0], [0, 0], [0, 1], color='C0', ls='-.')
ax.plot([0, R[0, 0]], [0, R[1, 0]], [0, R[2, 0]], color='C1', ls='-')
ax.plot([0, R[0, 1]], [0, R[1, 1]], [0, R[2, 1]], color='C1', ls='--')
ax.plot([0, R[0, 2]], [0, R[1, 2]], [0, R[2, 2]], color='C1', ls='-.')
plt.show()
