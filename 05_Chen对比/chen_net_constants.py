# Do Chen's success patterns depend on the arbitrary constants (initial activation 30, suppression threshold .001)?
# Same pseudo-test targets as chen_net_home.py (similarity-weighted networks, test 0, first 30 networks).
# For initial activation in {3, 30, 300} (threshold .001) and threshold 0, count combos (of 441) in which each target is activated,
# and the share of (r, d) pairs whose success on a target flips relative to the published setting (30, .001).
import glob, numpy as np, pandas as pd, scipy.sparse as sp
from multiprocessing import Pool
grid = np.round(np.arange(0, 1.0001, .05), 2); combos = np.array([(r, d) for r in grid for d in grid]); T = 100
SETTINGS = [(3, .001), (30, .001), (300, .001), (30, 0.0)]
def run(path):
    e = pd.read_csv(path); n = int(max(e.i.max(), e.j.max())) + 1
    W = sp.coo_matrix((np.r_[e.w, e.w], (np.r_[e.i, e.j], np.r_[e.j, e.i])), shape=(n, n)).tocsr()
    deg = np.asarray(W.sum(1)).ravel(); Pt = (sp.diags(1 / np.where(deg > 0, deg, 1)) @ W).T.tocsr()
    rng = np.random.default_rng(np.random.SeedSequence([7, int(path[-6:-4]), 0]))
    nodes = rng.choice(n, 4, replace=False); cues, tg = nodes[:3], nodes[3]      # same draw as chen_net_home.py, rep 0
    out = {}
    for a0, sup in SETTINGS:
        S = np.zeros(len(combos), bool)
        for k, (r, d) in enumerate(combos):
            A = np.zeros(n); A[cues] = a0
            for t in range(T):
                A = (1 - d) * (r * A + (1 - r) * (Pt @ A))
                if sup > 0: A[A < sup] = 0
                if A[tg] > 0: S[k] = True; break
                if not A.any(): break
        out[(a0, sup)] = S
    return out
if __name__ == '__main__':
    files = sorted(glob.glob('chen_nets/sim_*.csv'))[:30]
    with Pool(6) as p: res = p.map(run, files)
    base = np.array([r[(30, .001)] for r in res])
    for s in SETTINGS:
        M = np.array([r[s] for r in res])
        print(f'initial {s[0]:>3}, threshold {s[1]}: median combos activating target = {np.median(M.sum(1)):.0f} / 441;'
              f' share of (network, combo) cells whose success differs from (30, .001) = {np.mean(M != base):.3f}')
