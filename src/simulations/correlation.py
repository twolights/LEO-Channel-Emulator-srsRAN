import functools

import matplotlib.pyplot as plt
import numpy as np

N = 127
N_FFT = 128
NID2s = (0, 1, 2)
TO_CORRELATE = ((0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2))


def gamma(r: int, r_tilde: int, epsilon: int, Q: int) -> float:
    """
    r: NID2
    r_tilde: NID2 to be compared with
    epsilon: CFO in subcarrier spacing
    Q: difference between time offsets
    """
    return np.pi * (epsilon - 43 * (r - r_tilde) * Q) % N


def f(r: int, r_tilde: int, epsilon: int, Q: int, PSI: int) -> float:
    """
    PSI: number of iterations of MDCT
    """
    common = np.pi * gamma(r, r_tilde, epsilon, Q)
    if common == 0:
        return PSI
    return np.sin(common * PSI) / (PSI * np.sin(common))


f_parametrized = functools.partial(f, Q=1, PSI=6)

plt.figure(figsize=(10, 6))

subcarrier_spacings = range(-5, 5 + 1)
for nid2, nid2_tilde in TO_CORRELATE:
    y = [f_parametrized(nid2, nid2_tilde, epsilon=scs) for scs in subcarrier_spacings]
    plt.plot(subcarrier_spacings, y, label=f'NID2 pair ({nid2}, {nid2_tilde})')

# Add labels and title
plt.xlabel('Subcarrier Spacing')
plt.ylabel('f value')
plt.title('f values for Different NID2 Pairs and Subcarrier Spacings')
plt.legend()
plt.grid(True)
plt.show()
