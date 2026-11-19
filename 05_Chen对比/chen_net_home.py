# Chen's home turf on Chen's own item networks (TMFG rebuilt from their OSF matrices; both weight directions).
# The OSF package has no item key, so each pseudo-test takes, for each of the 80 networks, 3 random cue nodes and 1 random
# non-cue target node (the "answer"); 5 pseudo-tests per weight direction (seeded). For each pseudo-test we compute the
# 441 x 80 success matrix (target activated > 0 at any step, spreadr with Chen's settings) and the duration matrix, then
# simulate persons with true (r, d) uniform over the 400 pairs with r < 1 and d < 1, correct w.p. 1 - eps if success else eps,
# N = 46 (Chen's sample) and 100, eps = .05/.15/.25, 200 datasets each; estimate with Chen's rules (match share, duration
# tie-breaker). Reports distinct success patterns, Spearman r(true, est) for r and d, exact hits.
# Output: chen_net_home.csv, logs/chen_net_home.txt
import glob, numpy as np, pandas as pd, scipy.sparse as sp
from multiprocessing import Pool
from scipy.stats import spearmanr
grid = np.round(np.arange(0, 1.0001, .05), 2); combos = np.array([(r, d) for r in grid for d in grid]); T, SUP, REP = 100, .001, 5
def net_runs(path):
    e = pd.read_csv(path); n = int(max(e.i.max(), e.j.max())) + 1
    W = sp.coo_matrix((np.r_[e.w, e.w], (np.r_[e.i, e.j], np.r_[e.j, e.i])), shape=(n, n)).tocsr()
    deg = np.asarray(W.sum(1)).ravel(); Pt = (sp.diags(1 / np.where(deg > 0, deg, 1)) @ W).T.tocsr()
    rng = np.random.default_rng(np.random.SeedSequence([7, int(path[-6:-4]), 0 if 'sim_' in path else 1]))
    A0 = np.zeros((n, REP)); tg = []
    for c in range(REP):
        nodes = rng.choice(n, 4, replace=False); A0[nodes[:3], c] = 30; tg.append(nodes[3])
    tg = np.array(tg); S = np.zeros((len(combos), REP), bool); D = np.zeros((len(combos), REP))
    for k, (r, d) in enumerate(combos):
        A = A0.copy()
        for t in range(T):
            A = (1 - d) * (r * A + (1 - r) * (Pt @ A)); A[A < SUP] = 0
            a = A[tg, np.arange(REP)] > 0; S[k] |= a; D[k] += a
            if not A.any(): break
    return path, S, D
if __name__ == '__main__':
    out = []
    for wt in ['sim', 'dist']:
        files = sorted(glob.glob(f'chen_nets/{wt}_*.csv'))
        with Pool(6) as p: res = p.map(net_runs, files)
        S_all = np.stack([x[1] for x in res], 1); D_all = np.stack([x[2] for x in res], 1)   # 441 x 80 x REP
        np.savez_compressed(f'chen_net_S_{wt}.npz', S=S_all, D=D_all)
        pool = np.flatnonzero((combos[:, 0] < 1) & (combos[:, 1] < 1))
        for rep in range(REP):
            S = S_all[:, :, rep].astype(float); DUR = D_all[:, :, rep] * S_all[:, :, rep]; J = S.shape[1]
            npat = len({tuple(S[k]) for k in pool})
            for eps in (.05, .15, .25):
                for N in (46, 100):
                    for b in range(200):
                        rng = np.random.default_rng(np.random.SeedSequence([8, rep, int(eps * 100), N, b, wt == 'sim']))
                        tk = rng.choice(pool, N); corr = (rng.random((N, J)) < np.where(S[tk] == 1, 1 - eps, eps)).astype(float)
                        agree = corr @ S.T + (1 - corr) @ (1 - S).T; best = np.isclose(agree, agree.max(1, keepdims=True))
                        ek = np.argmax(np.where(best, np.ones((N, J)) @ DUR.T, -1), 1)
                        cr = lambda a, b2: np.nan if np.std(a) == 0 or np.std(b2) == 0 else spearmanr(a, b2)[0]
                        out.append(dict(weights=wt, test=rep, n_patterns=npat, eps=eps, N=N, rep=b,
                                        r_r=cr(combos[tk, 0], combos[ek, 0]), r_d=cr(combos[tk, 1], combos[ek, 1]),
                                        exact=np.mean(ek == tk), acc_mean=corr.mean()))
    o = pd.DataFrame(out); o.to_csv('chen_net_home.csv', index=False)
    print('Distinct success patterns among the 400 generating pairs (per pseudo-test):')
    print(o.groupby(['weights', 'test']).n_patterns.first().unstack().to_string())
    print('\nMedians over pseudo-tests x 200 datasets:')
    print(o.groupby(['weights', 'eps', 'N'])[['r_r', 'r_d', 'exact', 'acc_mean']].median().round(3).to_string())
