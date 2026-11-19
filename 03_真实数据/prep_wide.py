# Stan data for the wide breadth range. Two cue-combination scores:
#   sum  : log of joint activation = log mean_c a_c   (all cues spread together; model A)
#   prod : sum_c log a_c                              (multiply-constrained; models B-D)
# Chebyshev degree chosen as the smallest NC with max abs error < .01 on the grid.
import json, numpy as np
z = np.load('percue_v2.npz'); g = z['grid']; lo, hi = g[0], g[-1]; x = (2 * g - lo - hi) / (hi - lo)
cands = json.load(open('candidates.json'))
def score(kind, j):
    A = z[str(j)]
    return (np.logaddexp.reduce(A, 0) - np.log(3)) if kind == 'sum' else A.sum(0)
for kind in ['sum', 'prod']:
    for NC in [12, 16, 20, 24, 28]:
        B = np.polynomial.chebyshev.chebvander(x, NC - 1); err = 0; coefs = []
        for j in range(24):
            S = score(kind, j); cf = np.linalg.lstsq(B, S.T, rcond=None)[0].T; coefs.append(cf); err = max(err, np.abs(cf @ B.T - S).max())
        print(kind, 'NC', NC, 'max err %.4f' % err)
        if err < .01: break
    for smp in ['s1', 's2', 'pre']:
        d = json.load(open(f'stan_{smp}.json')); K = d['K']; C = np.zeros((24 * K, NC))
        for j, c in enumerate(cands): C[j * K: j * K + len(c)] = coefs[j]
        d.update(C=C.tolist(), D=NC, lo=float(lo), hi=float(hi)); json.dump(d, open(f'stan_{smp}_{kind}_w.json', 'w'))
