# Parameter-recovery pilot for model D on the real design (SWOW-EN18 network, 24 gfsb8 items, experiment-1 candidate sets,
# N = 100, experiment-1 missingness pattern). True population parameters are drawn uniformly from ranges around the
# estimates of the three real samples, so recovery is checked across a plausible region rather than at one point.
# Responses are generated with the same Chebyshev score the model uses (approximation error <= .008).
import json, sys, numpy as np
R = int(sys.argv[1]); rng = np.random.default_rng(20261110)
d = json.load(open('../03_真实数据/stan_s1_prod_w.json'))
N, J, K, D, lo, hi = d['N'], d['J'], d['K'], d['D'], d['lo'], d['hi']
C = np.array(d['C']); pad = np.array(d['pad']); nsol = d['nsol']; miss = np.array(d['yk']) < 0
ranges = dict(mu=(-1.5, .5), sigma=(1.5, 3.5), gamma=(.12, .18), kappa=(-2.2, -1.0), delta=(3.6, 4.3), tau=(.3, .9), rho=(-.2, .6))
sol = np.zeros(J * K)
for j in range(J): sol[j * K: j * K + nsol[j]] = 1
for r in range(R):
    t = {k: float(rng.uniform(*v)) for k, v in ranges.items()}
    z1, z2 = rng.standard_normal(N), rng.standard_normal(N)
    b = t['mu'] + t['sigma'] * z1; dv = t['delta'] + t['tau'] * (t['rho'] * z1 + np.sqrt(1 - t['rho'] ** 2) * z2)
    x = (2 * np.clip(b, lo, hi) - lo - hi) / (hi - lo)
    B = np.polynomial.chebyshev.chebvander(x, D - 1)          # N x D
    U = t['gamma'] * (B @ C.T) + pad + dv[:, None] * sol      # N x (J*K)
    yk = np.zeros((N, J), int)
    for j in range(J):
        v = np.column_stack([np.full(N, t['kappa']), U[:, j * K:(j + 1) * K]]); p = np.exp(v - v.max(1, keepdims=True)); p /= p.sum(1, keepdims=True)
        yk[:, j] = [rng.choice(K + 1, p=pi) for pi in p]
    yk[miss] = -1
    out = {k: d[k] for k in ['N', 'J', 'K', 'D', 'lo', 'hi', 'C', 'pad', 'nsol']}; out['yk'] = yk.tolist()
    json.dump(out, open(f'data/sim_{r:03d}.json', 'w'))
    json.dump(dict(t, b=b.tolist(), d=dv.tolist()), open(f'data/truth_{r:03d}.json', 'w'))
    acc = np.mean([(1 <= yk[i, j] <= nsol[j]) for i in range(N) for j in range(J) if yk[i, j] >= 0])
    print(r, 'acc %.3f' % acc, 'noans %.3f' % np.mean(yk[yk >= 0] == 0))
