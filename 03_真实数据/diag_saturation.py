# How much does the product score still change at the grid edges? (decides whether clamping beyond [lo,hi] is safe)
import json, numpy as np
z = np.load('percue.npz'); g = np.load('activation.npz')['grid']
lo_d, hi_d = [], []
for j in range(24):
    S = z[str(j)].sum(0); S = S - S.max(0)          # relative (what softmax sees)
    lo_d.append(np.abs(S[:, 1] - S[:, 0]).max()); hi_d.append(np.abs(S[:, -1] - S[:, -2]).max())
print('grid step', g[1] - g[0])
print('max |change| between last two grid points, low end: %.3f  high end: %.3f' % (max(lo_d), max(hi_d)))
th = 1 / (1 + np.exp(-g)); print('theta at ends', th[0].round(4), th[-1].round(4))
