
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

# Constants
r_0 = 1.0  # kpc
rho_0 = 1e-20  # kg/m^3
Phi = 1.618  # Golden ratio
G = 6.67430e-11  # m^3 kg^-1 s^-2
c_0 = 2.99792458e8  # m/s
kpc_to_m = 3.0857e19  # m/kpc
r_trans = 1e5  # kpc
t0 = 13.8e9  # years
t = 10e9     # years
alpha = 1.5
beta = 1.0
kappa = 0.1
r_planc = 1.616e-35 / kpc_to_m  # Planck length in kpc

# Radius array
r = np.logspace(-1, 3, 100)  # kpc (0.1 to 1000)
r_m = r * kpc_to_m  # Convert to meters

# Correction factors
f_density = (t0 / t)**alpha
f_strings = 1 / (1 + np.exp(-r_0 / r))

# Fractal density
rho = rho_0 * (r / r_0)**(-Phi) * f_density * f_strings

# Vortex velocity
v_m = 1e6 * (r / r_0)**(-Phi)  # m/s (example scaling)

# Variable speed of light
c = c_0 * np.tanh(1 - (G * rho * v_m**2) / c_0**2) * np.cos(2 * np.pi * np.log(r / r_0) / np.log(Phi)) * (1 + kappa * (r > r_trans))
c = np.maximum(c, 1e-10)  # Prevent division by zero

# Fractal cosmological constant
lambda_fractal = (8 * np.pi * G * rho_0 / c**2) * (r / r_0)**(-Phi) * np.cos(2 * np.pi * np.log(r / r_0) / np.log(Phi))

# Dark matter mass
M_DM = (4 * np.pi * rho_0 * (r_0 * kpc_to_m)**Phi / (3 - Phi)) * (r_m)**(3 - Phi)

# Metric differential equation for g_11
def metric_eqn(y, idx, M_DM, c, c_prime, lambda_fractal, r_m):
    idx = int(np.clip(idx, 0, len(r_m) - 1))
    r_val = r_m[idx]
    g_11 = y[0]
    if r_val < r_planc:
        return [np.inf]  # Singularity at Planck scale
    dg_11_dr = -2 * G * M_DM[idx] / (r_val**2 * (1 + g_11 * c_prime[idx] / c[idx])) - lambda_fractal[idx] * g_11
    return [dg_11_dr]

# Numerical integration
c_prime = np.gradient(c, r_m)
initial_g_11 = [1.0]
sol = odeint(metric_eqn, initial_g_11, range(len(r_m)), args=(M_DM, c, c_prime, lambda_fractal, r_m), mxstep=5000)
g_11 = sol[:, 0]
g_00 = -c**2 * (1 + lambda_fractal * r_m**2)

# Plot
plt.figure(figsize=(12, 8))

plt.subplot(2, 1, 1)
plt.loglog(r, g_11, label=r'$g_{11}$ (Cycle $t=10$ Gyr)', color='red')
plt.xlabel('Radius (kpc)')
plt.ylabel(r'$g_{11}$')
plt.title('Fractal Metric: $g_{11}$')
plt.grid(True)
plt.legend()

plt.subplot(2, 1, 2)
plt.loglog(r, -g_00, label=r'$g_{00}$ (Cycle $t=10$ Gyr)', color='blue')
plt.xlabel('Radius (kpc)')
plt.ylabel(r'$-g_{00}$')
plt.title('Fractal Metric: $g_{00}$')
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.savefig('figures/vortex_fractal.pdf', format='pdf', dpi=600)
plt.show()
