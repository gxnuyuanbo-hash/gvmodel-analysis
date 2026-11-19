# Generate one simulated dataset for the formal simulation (generalizes 04_参数还原/sim_D.py).
# Usage: python3 -I sim_gen.py <study> <cell> <rep_from> <rep_to>   (rep_to exclusive)
# Seeds: numpy SeedSequence([study_id, cell, rep]) so every dataset is reproducible on its own, independent of run order.
# Generating model: model D (product score, person verification d, (b, d) bivariate normal), same Chebyshev score as the fit.
# Missingness: each trial missing with probability .02 (rate of gfsb8 experiment 1). J = 12: random half of the 24 items.
# Careless responders (study s3): "random" picks uniformly among no-answer and the item's real candidates on every item;
# "giveup" gives no answer with probability .9 on each item, otherwise responds as the model says.
import json, sys, os, numpy as np
study, cell, r0, r1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
SID = {'s1': 1, 'sbc': 11, 's3': 3}[study]
spec = [c for c in json.load(open('cells.json')) if c['study'] == study and c['cell'] == cell][0]
base = json.load(open('../03_真实数据/stan_s1_prod_w.json'))
Jall, K, D, lo, hi = base['J'], base['K'], base['D'], base['lo'], base['hi']
C_all = np.array(base['C']).reshape(Jall, K, D); pad_all = np.array(base['pad']).reshape(Jall, K); nsol_all = np.array(base['nsol'])
UNI = dict(mu=(-1.5, .5), gamma=(.12, .18), kappa=(-2.2, -1.0), delta=(3.6, 4.3), tau=(.3, .9), rho=(-.2, .6))
def tnorm(rng, m, s, a=-np.inf, b=np.inf):
    while True:
        x = rng.normal(m, s)
        if a < x < b: return float(x)
def draw_truth(rng):
    if study == 'sbc':   # must equal the priors in breadth_unified_sbc.stan
        return dict(mu=float(rng.normal(-.5, .5)), sigma=tnorm(rng, 2.5, .5, 0), gamma=tnorm(rng, .15, .015, 0),
                    kappa=float(rng.normal(-1.6, .3)), delta=float(rng.normal(3.95, .18)), tau=tnorm(rng, .6, .15, 0),
                    rho=tnorm(rng, .2, .25, -1, 1))
    t = {k: float(rng.uniform(*v)) for k, v in UNI.items()}; t['sigma'] = spec['sigma']; return t
outdir = f'data/{study}/c{cell:02d}'; os.makedirs(outdir, exist_ok=True)
for rep in range(r0, r1):
    if os.path.exists(f'{outdir}/sim_{rep:04d}.json'): continue
    rng = np.random.default_rng(np.random.SeedSequence([SID, cell, rep]))
    N, J = spec['N'], spec['J']
    items = np.arange(Jall) if J == Jall else np.sort(rng.choice(Jall, J, replace=False))
    C = C_all[items].reshape(J * K, D); pad = pad_all[items].reshape(J * K); nsol = nsol_all[items]
    sol = np.zeros(J * K)
    for j in range(J): sol[j * K: j * K + nsol[j]] = 1
    t = draw_truth(rng)
    z1, z2 = rng.standard_normal(N), rng.standard_normal(N)
    b = t['mu'] + t['sigma'] * z1; dv = t['delta'] + t['tau'] * (t['rho'] * z1 + np.sqrt(1 - t['rho'] ** 2) * z2)
    x = (2 * np.clip(b, lo, hi) - lo - hi) / (hi - lo)
    U = t['gamma'] * (np.polynomial.chebyshev.chebvander(x, D - 1) @ C.T) + pad + dv[:, None] * sol
    yk = np.zeros((N, J), int)
    for j in range(J):
        v = np.column_stack([np.full(N, t['kappa']), U[:, j * K:(j + 1) * K]]); p = np.exp(v - v.max(1, keepdims=True)); p /= p.sum(1, keepdims=True)
        yk[:, j] = (p.cumsum(1) > rng.random(N)[:, None]).argmax(1)
    careless = np.zeros(N, bool)
    if spec['careless']:
        careless[rng.choice(N, int(round(spec['prop'] * N)), replace=False)] = True
        for i in np.flatnonzero(careless):
            for j in range(J):
                if spec['careless'] == 'random':
                    valid = np.flatnonzero(pad_all[items[j]] == 0) + 1; yk[i, j] = rng.choice(np.r_[0, valid])
                elif rng.random() < .9: yk[i, j] = 0
    yk[rng.random((N, J)) < .02] = -1
    allmiss = (yk < 0).all(1)
    if allmiss.any(): yk[allmiss, 0] = 0          # keep N fixed: a person with every trial missing gets one no-answer
    json.dump(dict(N=N, J=J, K=K, D=D, lo=lo, hi=hi, C=C.tolist(), pad=pad.tolist(), nsol=nsol.tolist(), yk=yk.tolist(),
                   items=items.tolist()), open(f'{outdir}/sim_{rep:04d}.json', 'w'))
    json.dump(dict(t, b=b.tolist(), d=dv.tolist(), careless=careless.tolist()), open(f'{outdir}/truth_{rep:04d}.json', 'w'))
