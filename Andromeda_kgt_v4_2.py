import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

# ---------------------------------------------------------
# KGT v4.2 – Optimierte Königsmann-Theory (ψ + Φ + Ω)
# ---------------------------------------------------------

# Konstanten
G = 4.30091e-6                  # Gravitationskonstante (kpc units)
M_b = 1.2e11                    # Baryonische Masse M31 (Msun)
soft = 0.6                      # Softening-Länge

# Optimierte Parameter (Theorie-konform)
gamma_psi = 1.35                # ψ-Verstärkung (reduziert für weniger inneren Boost)
eta0 = -0.22                    # ψ-Exponent innen
eta1 = -0.09                    # ψ-Exponent außen
eta_trans = 12.0                # Übergangsradius für η(r)

phi_amp = 4.2                   # Φ-Resonanz-Amplitude
phi_switch = 7.0                # Aktivierungsradius
phi_width = 3.8                 # Glätte des Gates
osc_amp = 0.30                  # Oszillationsamplitude
phi_log = 1.618034              # Goldener Schnitt für Log-Frequenz

Omega_amp = 46000.0             # Asymptotische Flachheit (~220 km/s Plateau)
rc = 5.8                        # Core-Suppression-Radius (r^6)

# Beobachtungsdaten
r_obs = np.array([1, 5, 10, 20, 30])
v_obs = np.array([170, 200, 225, 225, 220])
v_err = np.array([15, 10, 10, 10, 10])

# ---------------------------------------------------------
# Komponenten
# ---------------------------------------------------------

def a_newton(r):
    """Newtonsche baryonische Beschleunigung"""
    return G * M_b / (r + soft)**2

def eta_r(r):
    """Dynamischer ψ-Exponent"""
    return eta0 + (eta1 - eta0) * (1 - np.exp(-r / eta_trans))

def a_psi(r):
    """ψ-Backflow-Feld"""
    return gamma_psi * (r + soft)**eta_r(r)

def phi_gate(r):
    """Sanfte Aktivierung der Φ-Resonanz"""
    return 1 - np.exp(-(r / phi_switch)**phi_width)

def a_phi(r):
    """Φ-fraktale Resonanz mit log-harmonischer Oszillation"""
    osc = 1 + osc_amp * np.cos(2 * np.pi * np.log(r + soft) / np.log(phi_log))
    return phi_amp * osc * phi_gate(r) / (r + soft)**0.95

def a_omega(r):
    """Ω-asymptotischer Term mit scharfer Core-Dämpfung"""
    core_suppress = r**6 / (r**6 + rc**6)
    return Omega_amp / (r + soft) * core_suppress * phi_gate(r)

def a_total(r):
    """Gesamte effektive Beschleunigung (quadr. Superposition)"""
    return np.sqrt(a_newton(r)**2 + a_psi(r)**2 + a_phi(r)**2 + a_omega(r)**2)

def v_rot(r):
    """Rotationsgeschwindigkeit"""
    return np.sqrt(r * a_total(r))

# ---------------------------------------------------------
# Simulation
# ---------------------------------------------------------
r = np.linspace(0.5, 40, 1000)   # Höhere Auflösung für glattere Kurve
v_sim = v_rot(r)

# Interpolation auf Beobachtungspunkte
interp = interp1d(r, v_sim, fill_value="extrapolate")
v_model = interp(r_obs)

# Chi²-Bewertung
chi2 = np.sum(((v_model - v_obs) / v_err)**2)
dof = len(r_obs) - 3  # ca. 3 freie Parameter-Gruppen
chi2_red = chi2 / dof if dof > 0 else np.inf

# ---------------------------------------------------------
# Ausgabe
# ---------------------------------------------------------
print("\n--- KGT v4.2 – Optimierter Andromeda-Fit ---\n")
for ri, vo, vm in zip(r_obs, v_obs, v_model):
    print(f"r = {ri:>3} kpc | obs = {vo:6.1f} km/s | model = {vm:6.1f} km/s | diff = {vm - vo:+6.1f}")

print(f"\nChi² = {chi2:.2f}")
print(f"Reduced Chi² = {chi2_red:.2f}")

# ---------------------------------------------------------
# Plot
# ---------------------------------------------------------
plt.figure(figsize=(10, 6))
plt.plot(r, v_sim, label="KGT v4.2 (optimiert)", linewidth=3, color="navy")
plt.errorbar(r_obs, v_obs, yerr=v_err, fmt="o", color="red", markersize=8, label="Beobachtung")

# Optional: Komponenten einblenden
plt.plot(r, np.sqrt(r * a_newton(r)), "--", color="gray", alpha=0.6, label="Newtonian")
plt.plot(r, np.sqrt(r * a_psi(r)), ":", color="purple", alpha=0.6, label="ψ-Backflow")
plt.plot(r, np.sqrt(r * a_phi(r)), ":", color="gold", alpha=0.6, label="Φ-Resonanz")
plt.plot(r, np.sqrt(r * a_omega(r)), ":", color="green", alpha=0.6, label="Ω-Flat")

plt.xlabel("Radius r (kpc)")
plt.ylabel("Rotationsgeschwindigkeit v (km/s)")
plt.title("Andromeda Rotationskurve – Königsmann-Theory v4.2")
plt.grid(alpha=0.4)
plt.legend()
plt.tight_layout()
plt.show()
