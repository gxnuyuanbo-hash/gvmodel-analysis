# Replace C with Chebyshev fit of the product score sum_c log a_c(theta) (multiply-constrained combination).
import sys, json, numpy as np
z = np.load('percue.npz'); g = np.load('activation.npz')['grid']; cands = json.load(open('candidates.json'))
lo, hi = g[0], g[-1]; B = np.polynomial.chebyshev.chebvander((2 * g - lo - hi) / (hi - lo), 11)
for smp in ['s1', 's2', 'pre']:
    d = json.load(open(f'stan_{smp}.json')); K = d['K']; C = np.array(d['C']); err = 0
    for j, c in enumerate(cands):
        S = z[str(j)].sum(0)
        for k in range(len(c)):
            coef, *_ = np.linalg.lstsq(B, S[k], rcond=None); err = max(err, np.abs(B @ coef - S[k]).max()); C[j * K + k] = coef
    d['C'] = C.tolist(); json.dump(d, open(f'stan_{smp}_prod.json', 'w'))
print('max Chebyshev error', round(err, 4))
