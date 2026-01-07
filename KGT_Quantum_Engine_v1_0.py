import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

class KGTQuantumEngine:
    def __init__(self):
        # Constants
        self.r_0 = 1.0  # kpc
        self.rho_0 = 1e-20  # kg/m^3
        self.Phi = 1.618034
        self.G = 6.67430e-11
        self.c_0 = 2.99792458e8
        self.kpc_to_m = 3.0857e19
        self.r_trans = 1e5
        self.t0 = 13.8e9
        self.t = 10e9
        self.alpha = 1.5
        self.beta = 1.0
        self.kappa = 0.1
        self.r_planc = 1.616e-35 / self.kpc_to_m

        # Radius array
        self.r = np.logspace(-1, 3, 500)
        self.r_m = self.r * self.kpc_to_m

    def compute_density(self):
        f_density = (self.t0 / self.t)**self.alpha
        f_strings = 1 / (1 + np.exp(-self.r_0 / self.r))
        return self.rho_0 * (self.r / self.r_0)**(-self.Phi) * f_density * f_strings

    def compute_vortex_velocity(self):
        return 1e6 * (self.r / self.r_0)**(-self.Phi)

    def compute_c(self, rho, v_m):
        c = (
            self.c_0 *
            np.tanh(1 - (self.G * rho * v_m**2) / self.c_0**2) *
            np.cos(2 * np.pi * np.log(self.r / self.r_0 + 1e-10) / np.log(self.Phi)) *
            (1 + self.kappa * (self.r > self.r_trans))
        )
        return np.maximum(c, 1e-10)

    def compute_lambda(self, c):
        return (
            (8 * np.pi * self.G * self.rho_0 / c**2) *
            (self.r / self.r_0)**(-self.Phi) *
            np.cos(2 * np.pi * np.log(self.r / self.r_0 + 1e-10) / np.log(self.Phi))
        )

    def compute_M_DM(self):
        return (
            4 * np.pi * self.rho_0 * (self.r_0 * self.kpc_to_m)**self.Phi /
            (3 - self.Phi)
        ) * (self.r_m)**(3 - self.Phi)

    def metric_equation(self, idx, g11, c, lambda_frac, M_DM):
        r_val = self.r_m[idx]
        if r_val < self.r_planc:
            return 0
        c_prime = np.gradient(c, self.r_m)[idx]
        return -2 * self.G * M_DM[idx] / (r_val**2 * (1 + g11 * c_prime / c[idx])) - lambda_frac[idx] * g11

    def solve_metric(self):
        rho = self.compute_density()
        v_m = self.compute_vortex_velocity()
        c = self.compute_c(rho, v_m)
        lambda_frac = self.compute_lambda(c)
        M_DM = self.compute_M_DM()

        def ode_system(r_idx, y):
            idx = int(np.clip(r_idx, 0, len(self.r) - 1))
            return [self.metric_equation(idx, y[0], c, lambda_frac, M_DM)]

        sol = solve_ivp(
            ode_system,
            [0, len(self.r) - 1],
            [1.0],
            t_eval=np.arange(len(self.r)),
            method='RK45',
            max_step=1
        )

        g11 = sol.y[0]
        g00 = -c**2 * (1 + lambda_frac * self.r_m**2)
        return g11, g00, c, lambda_frac

    def plot(self, solution):
        g11, g00, c, lambda_frac = solution
        g00_plot = g00 / np.max(np.abs(g00))

        plt.figure(figsize=(12, 8))

        plt.subplot(2, 1, 1)
        plt.loglog(self.r, g11, label=r"$g_{11}$", color="red", linewidth=2)
        plt.xlabel("Radius (kpc)")
        plt.ylabel(r"$g_{11}$")
        plt.title("Fractal Metric: g11")
        plt.grid(True, which="both", ls="--", alpha=0.5)
        plt.legend()

        plt.subplot(2, 1, 2)
        plt.loglog(self.r, -g00_plot, label=r"$-g_{00}$ (scaled)", color="blue", linewidth=2)
        plt.xlabel("Radius (kpc)")
        plt.ylabel(r"$-g_{00}$")
        plt.title("Fractal Metric: g00 (renormalized)")
        plt.grid(True, which="both", ls="--", alpha=0.5)
        plt.legend()

        plt.tight_layout()
        plt.show()

# End of file
