# Per-cue activation on the wide breadth range logit [-10, 10] (81 points), exact for all theta:
#   theta <= .5 : plain series (1-theta) sum_t theta^t (P^T)^t a0           (no cancellation at small theta)
#   theta >  .5 : deflated series c*pi + (1-theta) sum_t theta^t (P^T)^t r,  r = a0 - pi (decays at rate ~.74)
# 250 steps in both cases (residual < 1e-15, see logs/diag_spectral.txt). Stores log a_c for candidates only.
import json, numpy as np, pandas as pd, scipy.sparse as sp
Pt = sp.load_npz('Pt.npz'); pi = np.load('pi.npy'); nodes = json.load(open('nodes.json')); idx = {w: i for i, w in enumerate(nodes)}
it = pd.read_csv('../01_数据/gfsb8/Data/items_characteristics.csv', sep=';'); cands = json.load(open('candidates.json'))
grid = np.linspace(-10, 10, 81); th = 1 / (1 + np.exp(-grid)); lowm = th <= .5; T = 250
out = {}
for j, p in enumerate(it.problem):
    ci = np.array([idx[w] for w in cands[j]]); res = []
    for c in p.lower().split('/'):
        a0 = np.zeros(len(pi)); a0[idx[c]] = 1
        acc_lo = np.zeros((len(ci), lowm.sum())); acc_hi = np.zeros((len(ci), (~lowm).sum()))
        v = a0.copy(); r = a0 - pi; pl = np.ones(lowm.sum()); ph = np.ones((~lowm).sum())
        for t in range(T):
            acc_lo += np.outer(v[ci], pl); acc_hi += np.outer(r[ci], ph)
            v = Pt @ v; r = Pt @ r; pl = pl * th[lowm]; ph = ph * th[~lowm]
        A = np.empty((len(ci), len(grid)))
        A[:, lowm] = acc_lo * (1 - th[lowm]); A[:, ~lowm] = pi[ci][:, None] + acc_hi * (1 - th[~lowm])
        res.append(np.log(np.maximum(A, 1e-300)))
    out[str(j)] = np.array(res)
np.savez_compressed('percue_v2.npz', grid=grid, **out)
# check against the old computation on the overlapping grid points
old = np.load('percue.npz'); g_old = np.load('activation.npz')['grid']; m = [int(np.argmin(abs(grid - x))) for x in g_old]
print('max |diff| vs old (logit -5..5):', max(np.abs(out[str(j)][:, :, m] - old[str(j)]).max() for j in range(24)))
print('min activation', min(out[str(j)].min() for j in range(24)))
