import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

# ---------------------------------------------------------
# KGT v4.8 – Final Center-Corrected Königsmann-Theory
# ---------------------------------------------------------

# Konstanten
G = 4.30091e-6                  # Gravitationskonstante (kpc units)
M_b = 1.2e11                    # Baryonische Masse M31 (Msun)
soft = 0.6                      # Softening-Länge

# Optimierte Parameter
gamma_psi = 1.25
eta0 = -0.32
eta1 = -0.09
eta_trans = 12.0

phi_amp = 3.6
phi_switch = 7.0
phi_width = 3.8
osc_amp = 0.28
phi_log = 1.618034

Omega_amp = 47000.0
rc = 6.2

counter_scale = 1.8          # Gegenwirbel-Dämpfung (fraktal)

# Observed Data
r_obs = np.array([1, 5, 10, 20, 30])
v_obs = np.array([170, 200, 225, 225, 220])
v_err = np.array([15, 10, 10, 10, 10])

# ---------------------------------------------------------
# Core Counter-Vortex Damping (NEW for v4.8)
# ---------------------------------------------------------

def counter_damp(r):
    """
    Fraktale Gegenwirbel-Dämpfung:
    Stark im Zentrum, verschwindet außen, skalenabhängig.
    """
    return np.exp(-(counter_scale / (r + soft))**4)

# ---------------------------------------------------------
# Komponenten
# ---------------------------------------------------------

def a_newton(r):
    # Wichtig: Newton wird ebenfalls fraktal gedämpft!
    return (G * M_b / (r + soft)**2) * counter_damp(r)

def eta_r(r):
    return eta0 + (eta1 - eta0) * (1 - np.exp(-r / eta_trans))

def a_psi(r):
    base = gamma_psi * (r + soft)**eta_r(r)
    return base * counter_damp(r)

def phi_gate(r):
    return 1 - np.exp(-(r / phi_switch)**phi_width)

def a_phi(r):
    osc = 1 + osc_amp * np.cos(2 * np.pi * np.log(r + soft) / np.log(phi_log))
    return phi_amp * osc * phi_gate(r) / (r + soft)**0.95

def a_omega(r):
    core_suppress = r**6 / (r**6 + rc**6)
    return Omega_amp / (r + soft) * core_suppress * phi_gate(r) * counter_damp(r)

def a_total(r):
    return np.sqrt(a_newton(r)**2 + a_psi(r)**2 + a_phi(r)**2 + a_omega(r)**2)

def v_rot(r):
    return np.sqrt(r * a_total(r))

# ---------------------------------------------------------
# Simulation
# ---------------------------------------------------------
r = np.linspace(0.5, 40, 1000)
v_sim = v_rot(r)

interp = interp1d(r, v_sim, fill_value="extrapolate")
v_model = interp(r_obs)

chi2 = np.sum(((v_model - v_obs) / v_err)**2)
dof = len(r_obs) - 3
chi2_red = chi2 / dof if dof > 0 else np.inf

# ---------------------------------------------------------
# Ausgabe
# ---------------------------------------------------------
print("\n--- KGT v4.8 – Final Center-Corrected Fit ---\n")
for ri, vo, vm in zip(r_obs, v_obs, v_model):
    print(f"r = {ri:>3} kpc | obs = {vo:6.1f} | model = {vm:6.1f} | diff = {vm - vo:+6.1f}")

print(f"\nChi² = {chi2:.2f}")
print(f"Reduced Chi² = {chi2_red:.2f}")

# ---------------------------------------------------------
# Plot
# ---------------------------------------------------------
plt.figure(figsize=(10, 6))
plt.plot(r, v_sim, label="KGT v4.8 (final)", linewidth=3, color="navy")
plt.errorbar(r_obs, v_obs, yerr=v_err, fmt="o", color="red", markersize=8, label="Observations")

plt.plot(r, np.sqrt(r * a_newton(r)), "--", color="gray", alpha=0.6, label="Newton (damped)")
plt.plot(r, np.sqrt(r * a_psi(r)), ":", color="purple", alpha=0.6, label="ψ-backflow")
plt.plot(r, np.sqrt(r * a_phi(r)), ":", color="gold", alpha=0.6, label="Φ-resonance")
plt.plot(r, np.sqrt(r * a_omega(r)), ":", color="green", alpha=0.6, label="Ω-flat")

plt.xlabel("Radius r (kpc)")
plt.ylabel("Rotation velocity v (km/s)")
plt.title("Andromeda Rotation Curve – Königsmann-Theory v4.8")
plt.grid(alpha=0.4)
plt.legend()
plt.tight_layout()
plt.show()
