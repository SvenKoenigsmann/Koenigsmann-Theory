import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

# ---------------------------------------------------------
# KGT v6.5 – Optimized Fractal Damping Model (Grok-refined)
# Focus: Balanced Core/Mid with minimized Chi²
# --------------------------------------------------------

# Constants
G = 4.30091e-6                  # Gravitational constant (kpc units)
M_b = 1.2e11                    # Baryonic mass M31 (Msun)
soft = 1.0                      # Optimized softening length (from 0.6)

# Optimized parameters (v6.5)
gamma_psi = 1.02                # Optimized ψ amplitude
eta0 = -0.43                    # Optimized core decay
eta1 = -0.09                    # Outer exponent
eta_trans = 10.0                # Transition radius

phi_amp = 1.8                   # Optimized Φ-resonance amplitude
phi_switch = 9.13               # Optimized resonance onset
phi_width = 3.8
osc_amp = 0.06                  # Optimized oscillation
phi_log = 1.618034              # Golden ratio

Omega_amp = 46500.0             # Ω-flat amplitude
rc = 6.0                        # Core suppression radius

counter_scale = 2.0             # Fractal damping
p = 5.0

counter_scale_newton = 2.62     # Optimized Newton damping scale
q = 2.0                         # Optimized Newton exponent (softer damping)

# Observed data
r_obs = np.array([1, 5, 10, 20, 30])
v_obs = np.array([170, 200, 225, 225, 220])
v_err = np.array([15, 10, 10, 10, 10])

# ---------------------------------------------------------
# Damping functions
# ---------------------------------------------------------

def counter_damp(r):
    return np.exp(-(counter_scale / (r + soft))**p)

def counter_damp_newton(r):
    return np.exp(-(counter_scale_newton / (r + soft))**q)

# ---------------------------------------------------------
# Model components
# ---------------------------------------------------------

def a_newton(r):
    return (G * M_b / (r + soft)**2) * counter_damp_newton(r)

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
    core = r**6 / (r**6 + rc**6)
    return Omega_amp / (r + soft) * core * phi_gate(r) * counter_damp(r)

def a_total(r):
    return np.sqrt(
        a_newton(r)**2 +
        a_psi(r)**2 +
        a_phi(r)**2 +
        a_omega(r)**2
    )

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
# Output
# ---------------------------------------------------------

print("\n--- KGT v6.5 – Optimized Fit ---\n")
for ri, vo, vm in zip(r_obs, v_obs, v_model):
    print(f"r = {ri:>3} kpc | obs = {vo:6.1f} | model = {vm:6.1f} | diff = {vm - vo:+6.1f}")

print(f"\nChi² = {chi2:.2f}")
print(f"Reduced Chi² = {chi2_red:.2f}")

# ---------------------------------------------------------
# Plot
# ---------------------------------------------------------

plt.figure(figsize=(10, 6))
plt.plot(r, v_sim, label="KGT v6.5", linewidth=3, color="navy")
plt.errorbar(r_obs, v_obs, yerr=v_err, fmt="o", color="red", markersize=8, label="Observed")

plt.plot(r, np.sqrt(r * a_newton(r)), "--", color="gray", alpha=0.6, label="Newton (damped)")
plt.plot(r, np.sqrt(r * a_psi(r)), ":", color="purple", alpha=0.6, label="ψ-Backflow")
plt.plot(r, np.sqrt(r * a_phi(r)), ":", color="gold", alpha=0.6, label="Φ-Resonance")
plt.plot(r, np.sqrt(r * a_omega(r)), ":", color="green", alpha=0.6, label="Ω-Flat")

plt.xlabel("Radius r (kpc)")
plt.ylabel("Rotation velocity v (km/s)")
plt.title("Andromeda Rotation Curve – Königsmann-Theory v6.5")
plt.grid(alpha=0.4)
plt.legend()
plt.tight_layout()
plt.show()
