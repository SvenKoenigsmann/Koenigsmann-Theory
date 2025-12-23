import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

# ---------------------------------------------------------
# KGT v3.5 – Königsmann-Theory (ψ + Φ + Ω, scientifically tuned)
# ---------------------------------------------------------

# Gravitational constant in kpc*(km/s)^2/Msun
G = 4.30091e-6

# Baryonic mass of Andromeda (Msun)
M_b = 1.2e11

# Global softening
soft = 0.6

# --- Tuned parameters (v3.5) ---
gamma = 1.35        # reduced ψ strength
eta0  = -0.18        # inner psi exponent
eta1  = -0.10        # outer psi exponent

phi_amp = 3.5        # harmonic amplitude reduced
k_phi   = 0.90       # oscillation frequency
A0      = 0.25       # base oscillation amplitude
A1      = 0.45       # outer oscillation amplitude

Omega_amp = 48000.0  # asymptotic flatness term
rc = 6.0             # inner core suppression scale (sharp)

phi_switch = 8.0     # where Φ activates
phi_width  = 2.3     # smoothness of activation

# ---------------------------------------------------------
# OBSERVED DATA
# ---------------------------------------------------------
r_obs = np.array([1, 5, 10, 20, 30])
v_obs = np.array([170, 200, 225, 225, 220])
v_err = np.array([15, 10, 10, 10, 10])

# ---------------------------------------------------------
# KGT COMPONENTS
# ---------------------------------------------------------

# Newtonian baryonic acceleration
def a_newton(r):
    return G * M_b / (r + soft)**2


# Smooth transition for eta(r)
def eta_r(r):
    return eta0 + (eta1 - eta0) * (1 - np.exp(-r / 12))


# ψ-Backflow, now with inner damping
def a_psi(r):
    transition = 1 - np.exp(-r / 7)
    core_damp = r**4 / (r**4 + 2.5**4)  # suppress inner divergence
    base = (r + soft)**eta_r(r)
    return gamma * base * transition * core_damp


# Φ-Gate (activates at mid radii)
def phi_gate(r):
    return 1 - np.exp(- (r / phi_switch)**phi_width)


# Oscillation amplitude A(r)
def A_r(r):
    return A0 + (A1 - A0) * (1 - np.exp(-r / 15))


# Φ-harmonic Resonance (fractal)
def a_phi(r):
    osc = 1 + A_r(r) * np.cos(k_phi * np.log(r + soft))
    return phi_amp * osc * phi_gate(r) / (r + soft)**0.9


# Ω-flat (asymptotic), strongly inner-suppressed
def a_omega(r):
    core_s = r**6 / (r**6 + rc**6)
    return Omega_amp / (r + soft) * core_s


# Total acceleration (quadrature as in v3.x)
def a_total(r):
    return np.sqrt(a_newton(r)**2 + a_psi(r)**2 + a_phi(r)**2 + a_omega(r)**2)


# Circular velocity
def v_total(r):
    return np.sqrt(r * a_total(r))


# ---------------------------------------------------------
# SIMULATION
# ---------------------------------------------------------
r = np.linspace(0.5, 40, 600)
v_sim = v_total(r)

interp = interp1d(r, v_sim, fill_value="extrapolate")
v_model_at_obs = interp(r_obs)

# Chi²
chi2 = np.sum(((v_model_at_obs - v_obs) / v_err)**2)
chi2_red = chi2 / (len(r_obs) - 3)

# OUTPUT
print("\n--- KGT v3.5 – Andromeda Simulation ---\n")
for ri, vo, vm in zip(r_obs, v_obs, v_model_at_obs):
    print(f"r = {ri:>3} kpc | obs = {vo:>6.1f} km/s | KGT = {vm:>6.1f} km/s | diff = {vm-vo:+6.1f}")

print(f"\nChi² = {chi2:.2f}")
print(f"Reduced Chi² = {chi2_red:.2f}")

# PLOT
plt.figure(figsize=(10,6))
plt.plot(r, v_sim, label="KGT v3.5", linewidth=3, color="royalblue")
plt.errorbar(r_obs, v_obs, yerr=v_err, fmt='o', color='red', markersize=8, label="Observed")

plt.plot(r, np.sqrt(r*a_newton(r)), "--", color="gray", alpha=0.5, label="Newtonian")
plt.xlabel("Radius r (kpc)")
plt.ylabel("Rotation Speed v (km/s)")
plt.title("Andromeda Rotation Curve – Königsmann-Theory v3.5")
plt.grid(alpha=0.4)
plt.legend()
plt.tight_layout()
plt.show()
