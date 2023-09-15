import pathlib

import matplotlib.pyplot as plt
import numpy as np

import powerfit

root = pathlib.Path(__file__).parent
basename = pathlib.Path(__file__).stem

fig, axes = plt.subplots(ncols=2)

for ax in axes:
    ax.set_xscale("log")
    ax.set_yscale("log")

x = np.logspace(1, 5, 100)
y = 1.2 * x**-3.4 * np.exp(-x / 1e4)

fit = powerfit.powerlaw(x, y, exponent=-3.4, cutoff_upper=-1)
p = fit["prefactor"] * x ** fit["exponent"]
print(fit["slice"])

axes[0].plot(x, y, c="k", marker=".")
axes[0].plot(x, p, c="r")

y = np.logspace(1, 5, 100)
x = 1.2 * y**-3.4 * np.exp(-y / 1e4)
sorter = np.argsort(x)
x = x[sorter]
y = y[sorter]

fit = powerfit.powerlaw(x, y, cutoff_lower=-1)
p = fit["prefactor"] * x ** fit["exponent"]
s = fit["slice"]

axes[1].plot(x, y, c="k", marker=".")
axes[1].plot(x, p, c="r")

plt.savefig(root / (basename + ".png"))
plt.close(fig)
