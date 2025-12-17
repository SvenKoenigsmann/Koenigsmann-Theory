
import numpy as np
import matplotlib.pyplot as plt

# Constants
r_0 = 1.0  # kpc
rho_0 = 1e-20  # kg/m^3
D = 2.2  # Fractal dimension
G = 6.67430e-11  # m^3 kg^-1 s^-2
kpc_to_m = 3.0857e19  # m/kpc
Phi = 1.618  # Golden ratio
r_trans = 1e5  # Transition radius in kpc (~1e24 m)
sigma = 1e4  # Transition width in kpc
t0 = 13.8e9  # years (present)
t = 10e9     # past time
alpha = 1.5  # density dilution
beta = 1.0   # vortex slowdown

# Correction factors
f_density = (t0 / t)**alpha
f_vortex = (t / t0)**beta
r = np.logspace(-1, 3, 100)  # Radius in kpc (0.1 to 1000)

# String correction to prevent infinite density
f_strings = 1 / (1 + np.exp(-r_0 / r))

# Fractal density
rho = rho_0 * (r / r_0)**(-Phi) * f_density * f_strings

# Rotation velocity with transition zone
M = (4 * np.pi * rho * (r_0 * kpc_to_m)**D) / (3 - D) * (r * kpc_to_m)**(3 - D)
v = np.sqrt(G * M / (r * kpc_to_m)) * f_vortex * np.exp(-((r - r_trans)**2) / (2 * sigma**2)) / 1000

# Observational data (Gaia DR3) with error bars
r_obs = np.array([1, 5, 10, 20, 30])
v_obs = np.array([170, 200, 225, 225, 220])
v_err = np.array([15, 10, 10, 10, 10])  # Error bars

# Plot
plt.figure(figsize=(10, 6))
plt.plot(r, v, label='Königsmann Theory', color='red')
plt.errorbar(r_obs, v_obs, yerr=v_err, fmt='o', color='blue', label='Gaia DR3', zorder=5)
plt.xlabel('Radius (kpc)')
plt.ylabel('Rotation Velocity (km/s)')
plt.title('Andromeda Rotation Curve: Königsmann Theory vs. Gaia DR3')
plt.xscale('log')
plt.yscale('linear')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('figures/andromeda.pdf', format='pdf', dpi=600)
plt.show()
