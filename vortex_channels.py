
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Constants
Phi = 1.618  # Golden ratio
r_0 = 1.0  # kpc
theta_max = 2 * np.pi * 3  # 3 full rotations
n_points = 100

# Parametric equations for egg-shaped vortex channel
theta = np.linspace(0, theta_max, n_points)
r = r_0 * np.exp(theta / np.log(Phi))  # Logarithmic spiral
x = r * np.cos(theta) * (1 + 0.3 * np.sin(theta))  # Egg-shaped modulation
y = r * np.sin(theta) * (1 + 0.3 * np.sin(theta))
z = r * np.cos(theta / Phi)  # Z-axis oscillation for 3D effect

# Backflow direction (arrows)
t_arrow = np.linspace(0, theta_max, 10)
r_arrow = r_0 * np.exp(t_arrow / np.log(Phi))
x_arrow = r_arrow * np.cos(t_arrow) * (1 + 0.3 * np.sin(t_arrow))
y_arrow = r_arrow * np.sin(t_arrow) * (1 + 0.3 * np.sin(t_arrow))
z_arrow = r_arrow * np.cos(t_arrow / Phi)
dx = -np.gradient(x_arrow)  # Backflow direction (opposite to main flow)
dy = -np.gradient(y_arrow)
dz = -np.gradient(z_arrow)

# Plot
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
ax.plot(x, y, z, 'r-', label='Egg-Shaped Vortex Channel')
ax.quiver(x_arrow, y_arrow, z_arrow, dx, dy, dz, color='blue', length=0.5, normalize=True, label='Backflow Direction')
ax.set_xlabel('X (kpc)')
ax.set_ylabel('Y (kpc)')
ax.set_zlabel('Z (kpc)')
ax.set_title('3D Egg-Shaped Vortex Channels with Backflow')
ax.legend()
plt.tight_layout()
plt.savefig('figures/vortex_channels.pdf', format='pdf', dpi=600)
plt.show()
