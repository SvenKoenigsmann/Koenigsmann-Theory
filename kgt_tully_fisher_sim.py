import numpy as np
import matplotlib.pyplot as plt

# -------------------------------------------
# Parameter (Königsmann Theorie)
# -------------------------------------------
gamma = 1.18
eta = -0.16
D = 2.6

# Theoretischer KGT-Exponent
x_kgt = (2 * D) / (1 + eta)
x_std = 4.0  # Standard BTFR / MOND Referenz

# -------------------------------------------
# Simulation
# -------------------------------------------
v = np.logspace(np.log10(20), np.log10(300), 200)

A_kgt = 10**10 / (100**x_kgt)
A_std = 10**10 / (100**x_std)

Mb_kgt = A_kgt * v**x_kgt
Mb_std = A_std * v**x_std

# Realistisches Messrauschen
noise = np.random.normal(1.0, 0.08, len(v))
Mb_kgt_noisy = Mb_kgt * noise

# -------------------------------------------
# Fit
# -------------------------------------------
coeffs = np.polyfit(np.log10(v), np.log10(Mb_kgt_noisy), 1)
slope_fitted = coeffs[0]
intercept_fitted = coeffs[1]

# -------------------------------------------
# Plot
# -------------------------------------------
plt.figure(figsize=(10, 6))

plt.scatter(v, Mb_kgt_noisy, s=15, alpha=0.5, color='royalblue',
            label=f"KGT Simulation (Theorie x ≈ {x_kgt:.2f})")

plt.loglog(v, 10**intercept_fitted * v**slope_fitted, color='darkblue',
           linewidth=2, label=f"KGT Fit: Steigung = {slope_fitted:.2f}")

plt.loglog(v, Mb_std, color='crimson', linestyle='--', linewidth=2,
           label="Standard BTFR (x = 4.0)")

plt.xlabel("Rotation Velocity v_rot (km/s)")
plt.ylabel("Baryonic Mass M_b (M_sun)")
plt.title("Baryonic Tully-Fisher Relation: KGT vs. Standardmodell")

formula_text = (r"$x_{KGT} = rac{2D}{1+\eta}$" + "\n" +
                f"$x_{{calc}} = {x_kgt:.2f}$")

plt.text(0.05, 0.92, formula_text, transform=plt.gca().transAxes,
         fontsize=12, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

plt.grid(True, which="both", ls=":", alpha=0.6)
plt.legend(loc="lower right")
plt.tight_layout()
plt.show()

print("Ergebnis-Check:")
print(f"-> Erwarteter Exponent (KGT): {x_kgt:.3f}")
print(f"-> Realisierter Exponent im Fit: {slope_fitted:.3f}")
