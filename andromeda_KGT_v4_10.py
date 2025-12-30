import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

# ============================================================================
# KGT v4.12 — Final Optimized Vortex-Backflow Model
# ============================================================================

G = 4.30091e-6
M_b = 1.2e11
soft = 0.6

r_obs = np.array([1, 5, 10, 20, 30])
v_obs = np.array([170, 200, 225, 225, 220])
v_err = np.array([15, 10, 10, 10, 10])

# ============================================================================
# Optimized parameters (based on 4.11 refinement)
# ============================================================================

VORTEX_SPACING = 3.4
VORTEX_DECAY = 0.48
VORTEX_PHASE = 1.8

BACKFLOW_STRENGTH = 0.78
BACKFLOW_CUTOFF = 15.0

PHI_QUANTUM = 2.4
PHI_AMPLITUDE = 2.85
PHI_WIDTH = 4.0

OMEGA_BASE = 48000
OMEGA_CUTOFF = 8.5

COUNTER_STRENGTH = 1.8
COUNTER_WIDTH = 1.2

# ============================================================================
# Components
# ============================================================================

def vortex_distribution(r):
    n = int(40 // VORTEX_SPACING) + 1
    positions = np.array([i * VORTEX_SPACING for i in range(1, n + 1)])
    strength = VORTEX_DECAY ** np.arange(n)
    total = np.zeros_like(r)
    for p, s in zip(positions, strength):
        total += s * np.exp(-((r - p) / (VORTEX_SPACING*0.6))**2)
    return total / np.max(total)

def fractal_backflow(r):
    x = r / BACKFLOW_CUTOFF
    return BACKFLOW_STRENGTH * (1 - np.tanh(3 * (x - 0.7))) * 0.5

def phi_resonance_quantized(r):
    steps = np.floor(r / PHI_QUANTUM)
    blend = 0.5 * (1 + np.sin(2*np.pi*(r/PHI_QUANTUM - 0.25)))
    base = PHI_AMPLITUDE * np.exp(-(r / PHI_WIDTH)**2)
    return base * (0.7 + 0.3 * blend)

def counter_vortex_damping(r):
    return 1.0 - COUNTER_STRENGTH * np.exp(-(r / COUNTER_WIDTH)**2)

def omega_flattening(r):
    trans = r**6 / (r**6 + OMEGA_CUTOFF**6)
    return OMEGA_BASE / (r + soft) * trans

# ============================================================================
# Acceleration terms
# ============================================================================

def a_newton(r):
    return (G*M_b/(r+soft)**2) * (1 + 0.3*vortex_distribution(r)) * counter_vortex_damping(r)

def a_psi(r):
    return 1.15 * fractal_backflow(r) * (1 + 0.4*vortex_distribution(r)) * (r+soft)**0.45

def a_phi(r):
    phi_res = phi_resonance_quantized(r)
    phase = 1.0 + 0.18*np.sin(2*np.pi*r/(PHI_QUANTUM*2) + VORTEX_PHASE)
    return phi_res * phase / (r+soft)**0.88

def a_omega(r):
    return omega_flattening(r) * (1 - 0.5*np.exp(-(r/12)**2))

def a_total(r):
    return np.sqrt(a_newton(r)**2 + a_psi(r)**2 + a_phi(r)**2 + a_omega(r)**2)

def v_rot(r):
    return np.sqrt(r * a_total(r))

# ============================================================================
# Fit
# ============================================================================

r_fine = np.linspace(0.5, 40, 800)
v_sim = v_rot(r_fine)

interp = interp1d(r_fine, v_sim, kind="cubic", fill_value="extrapolate")
v_model = interp(r_obs)

chi2 = np.sum(((v_model - v_obs)/v_err)**2)
dof = max(1, len(r_obs) - 2)
chi2_red = chi2 / dof

# ============================================================================
# Output
# ============================================================================

print("\nKGT v4.12 — Final Optimized Model")
for ri, vo, vm in zip(r_obs, v_obs, v_model):
    print(f"{ri:>3} kpc | obs={vo:6.1f} | model={vm:6.1f} | diff={vm-vo:+.1f}")

print(f"\nChi² = {chi2:.2f}")
print(f"Reduced Chi² = {chi2_red:.2f}")
