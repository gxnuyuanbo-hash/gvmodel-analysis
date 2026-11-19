# Chen's home turf on Chen's own networks with the REAL CWRAT items: cues = first 3 nodes of each item network (what Chen et al.
# activated), target = reference answer from 陈静等 (2024) appendix (chen_key.csv; 76 of 80 answers are network nodes).
# Both weight directions (similarity / distance TMFG). For each: (1) success and duration matrices over 441 combos with Chen's
# settings (initial 30, 100 steps, suppress .001); (2) the same with initial 3 and 300 and with no suppression; (3) home-turf
# recovery: persons with true (r, d) over the 400 non-degenerate pairs, correct w.p. 1 - eps if success else eps, N = 46 / 100,
# eps = .05/.15/.25, 1,000 datasets each, estimated with Chen's rules. Output: chen_real_home.csv, logs/chen_real_home.txt
import numpy as np, pandas as pd, scipy.sparse as sp
from multiprocessing import Pool
from scipy.stats import spearmanr
grid = np.round(np.arange(0, 1.0001, .05), 2); combos = np.array([(r, d) for r in grid for d in grid]); T = 100
key = pd.read_csv('chen_key.csv'); key = key[key.answer_in_net].reset_index(drop=True)
SETTINGS = [(30, .001), (3, .001), (300, .001), (30, 0.0)]
def run(args):
    wt, k, tg = args
    e = pd.read_csv(f'chen_nets/{wt}_{k:02d}.csv'); n = int(max(e.i.max(), e.j.max())) + 1
    W = sp.coo_matrix((np.r_[e.w, e.w], (np.r_[e.i, e.j], np.r_[e.j, e.i])), shape=(n, n)).tocsr()
    deg = np.asarray(W.sum(1)).ravel(); Pt = (sp.diags(1 / np.where(deg > 0, deg, 1)) @ W).T.tocsr()
    res = {}
    for a0, sup in SETTINGS:
        S = np.zeros(len(combos), bool); D = np.zeros(len(combos))
        for c, (r, d) in enumerate(combos):
            A = np.zeros(n); A[[0, 1, 2]] = a0
            for t in range(T):
                A = (1 - d) * (r * A + (1 - r) * (Pt @ A))
                if sup > 0: A[A < sup] = 0
                if A[tg] > 0: S[c] = True; D[c] += 1
                if not A.any(): break
        res[(a0, sup)] = (S, D)
    return wt, k, res
if __name__ == '__main__':
    jobs = [(wt, int(r.id) - 1, int(r.answer_idx)) for wt in ('sim', 'dist') for _, r in key.iterrows()]
    with Pool(6) as p: out = p.map(run, jobs)
    pool = np.flatnonzero((combos[:, 0] < 1) & (combos[:, 1] < 1)); rows = []
    for wt in ('sim', 'dist'):
        R = [o[2] for o in out if o[0] == wt]
        S = np.array([x[(30, .001)][0] for x in R]).T.astype(float); DUR = np.array([x[(30, .001)][1] for x in R]).T * S   # 441 x 76
        np.savez_compressed(f'chen_real_S_{wt}.npz', S=S, DUR=DUR)
        print(f'\n=== {wt} weights, {S.shape[1]} real items ===')
        print('distinct success patterns among the 400 non-degenerate pairs:', len({tuple(S[c]) for c in pool}))
        print('median combos (of 441) activating the answer:', np.median(S.sum(0)), '| items activated in all 400:', int((S[pool].sum(0) == 400).sum()))
        for s in SETTINGS[1:]:
            M = np.array([x[s][0] for x in R]).T
            print(f'  initial {s[0]}, threshold {s[1]}: median combos activating answer = {np.median(M.sum(0)):.0f};'
                  f' share of (item, combo) success judgements that flip vs (30, .001) = {np.mean(M[pool] != (S[pool] == 1)):.3f}')
        J = S.shape[1]
        for eps in (.05, .15, .25):
            for N in (46, 100):
                for b in range(1000):
                    rng = np.random.default_rng(np.random.SeedSequence([9, int(eps * 100), N, b, wt == 'sim']))
                    tk = rng.choice(pool, N); corr = (rng.random((N, J)) < np.where(S[tk] == 1, 1 - eps, eps)).astype(float)
                    agree = corr @ S.T + (1 - corr) @ (1 - S).T; best = np.isclose(agree, agree.max(1, keepdims=True))
                    ek = np.argmax(np.where(best, np.ones((N, J)) @ DUR.T, -1), 1)
                    cr = lambda a, b2: np.nan if np.std(a) == 0 or np.std(b2) == 0 else spearmanr(a, b2)[0]
                    rows.append(dict(weights=wt, eps=eps, N=N, rep=b, r_r=cr(combos[tk, 0], combos[ek, 0]), r_d=cr(combos[tk, 1], combos[ek, 1]),
                                     exact=np.mean(ek == tk), acc=corr.mean(), r_acc=cr(corr.mean(1), combos[ek, 1])))
    o = pd.DataFrame(rows); o.to_csv('chen_real_home.csv', index=False)
    print('\nHome-turf recovery with real items, medians over 1,000 datasets (Spearman r):')
    print(o.groupby(['weights', 'eps', 'N'])[['r_r', 'r_d', 'exact', 'acc', 'r_acc']].median().round(3).to_string())
