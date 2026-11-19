# Reimplementation of Chen et al. (2026, BRM) spreading activation on the SWOW-EN18 R123 network, following spreadr
# (Siew, 2019; source R/spreadr.R): each step a <- (1-d) * (r*a + (1-r) * P^T a), then values below the suppression
# threshold are set to 0. Settings as reported by Chen et al.: initial activation 30 on each cue, 100 steps,
# suppress = .001, retention r and decay d each 0..1 in steps of .05 (441 combinations).
# P is the same row-normalized symmetrized weight matrix used by our model (spreadr divides by weighted degree).
# Output for each combination and item: whether any solution node is activated (>0) at any step 1..100 (main rule),
# whether it is activated at step 100 (sensitivity rule), the max solution activation, and the activation duration
# (number of steps with solution activation > 0), used by Chen et al. as tie-breaker.
import json, sys, numpy as np, pandas as pd, scipy.sparse as sp
from multiprocessing import Pool
base = '../03_真实数据/'
Pt = sp.load_npz(base + 'Pt.npz').tocsr().astype(np.float64); nodes = json.load(open(base + 'nodes.json')); idx = {w: i for i, w in enumerate(nodes)}
it = pd.read_csv('../01_数据/gfsb8/Data/items_characteristics.csv', sep=';'); cands = json.load(open(base + 'candidates.json'))
nsol = json.load(open(base + 'stan_s1_prod_w.json'))['nsol']
J = len(it); A0 = np.zeros((len(nodes), J))
for j, p in enumerate(it.problem):
    for c in p.lower().split('/'): A0[idx[c], j] += 30
sol = [np.array([idx[w] for w in cands[j][:nsol[j]]]) for j in range(J)]
grid = np.round(np.arange(0, 1.0001, .05), 2); T, SUP = 100, .001

def run(rd):
    r, d = rd; A = A0.copy(); anyact = np.zeros(J, bool); mx = np.zeros(J); dur = np.zeros(J)
    for t in range(T):
        A = (1 - d) * (r * A + (1 - r) * (Pt @ A)); A[A < SUP] = 0
        s = np.array([A[sol[j], j].max() for j in range(J)]); anyact |= s > 0; mx = np.maximum(mx, s); dur += s > 0
        if not A.any(): break
    final = np.array([A[sol[j], j].max() > 0 for j in range(J)])
    return anyact, final, mx, dur

if __name__ == '__main__':
    combos = [(r, d) for r in grid for d in grid]
    with Pool(6) as pool: res = pool.map(run, combos)
    S_any = np.array([x[0] for x in res]); S_fin = np.array([x[1] for x in res]); M = np.array([x[2] for x in res]); DUR = np.array([x[3] for x in res])
    np.savez_compressed('chen_S.npz', combos=np.array(combos), S_any=S_any, S_fin=S_fin, maxact=M, dur=DUR)
    for name, S in [('any step', S_any), ('step 100', S_fin)]:
        pats = {tuple(s) for s in S}
        print(f'rule {name}: distinct success patterns over 441 combos = {len(pats)}; '
              f'items ever activated = {S.any(0).sum()}/{J}; combos activating all items = {S.all(1).sum()}; combos activating none = {(~S).all(1).sum()}')
    print('mean items activated by d (rows) averaged over r:')
    print(pd.Series(S_any.reshape(21, 21, J).sum(2).mean(0), index=grid).round(1).to_string())
