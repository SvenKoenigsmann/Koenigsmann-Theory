
import numpy as np
import matplotlib.pyplot as plt

# Constants
r_0 = 1.0  # kpc
rho_0 = 1e-20  # kg/m^3
Phi = 1.618  # Golden ratio
gamma = 0.01  # Backflow amplitude (dimensionless)
kpc_to_m = 3.0857e19  # m/kpc

# Radius array
r = np.linspace(0.1, 50, 500)  # kpc (0.1 to 50)

# Density profiles
rho_nfw = rho_0 / (r / r_0)  # NFW profile, normalized
rho_fractal = gamma * rho_0 * (r / r_0)**(-Phi) * (1 - np.exp(-r / r_0))  # Königsmann fractal backflow

# Plot
plt.figure(figsize=(10, 6))
plt.plot(r, rho_nfw, 'b--', label=r'$\Lambda$CDM (NFW)')
plt.plot(r, rho_fractal, 'r-', label='Königsmann Theory')
plt.xlabel('Radius (kpc)')
plt.ylabel('DM Density (kg/m³)')
plt.title('Dark Matter Density: Königsmann Theory vs. $\Lambda$CDM (NFW)')
plt.yscale('log')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig('figures/dm_backflow.pdf', format='pdf', dpi=600)
plt.show()
