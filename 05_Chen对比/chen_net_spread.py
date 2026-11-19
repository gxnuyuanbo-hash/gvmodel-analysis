# spreadr dynamics on Chen et al.'s own item networks (TMFG-filtered, rebuilt by chen_net_tmfg.R), both weight directions.
# The OSF package has no item key (cues and answers), so cues are 3 randomly chosen nodes (5 replicates per network),
# and every other node is treated as a possible target. For each target node we count the combos (of 441) in which it is
# activated (> 0) at any step 1..100, i.e. the success criterion of Chen et al. This tells whether, on their networks,
# success varies across the (r, d) grid at all, regardless of which word the answer is.
import glob, numpy as np, pandas as pd, scipy.sparse as sp
from multiprocessing import Pool
grid = np.round(np.arange(0, 1.0001, .05), 2); combos = [(r, d) for r in grid for d in grid]; T, SUP, REP = 100, .001, 5
def one(path):
    e = pd.read_csv(path); n = int(max(e.i.max(), e.j.max())) + 1
    W = sp.coo_matrix((np.r_[e.w, e.w], (np.r_[e.i, e.j], np.r_[e.j, e.i])), shape=(n, n)).tocsr()
    deg = np.asarray(W.sum(1)).ravel(); Pt = (sp.diags(1 / np.where(deg > 0, deg, 1)) @ W).T.tocsr()
    rng = np.random.default_rng(abs(hash(path[-10:])) % 2**32); A0 = np.zeros((n, REP)); cues = []
    for c in range(REP):
        cc = rng.choice(n, 3, replace=False); A0[cc, c] = 30; cues.append(cc)
    hit = np.zeros((len(combos), n, REP), bool)
    for k, (r, d) in enumerate(combos):
        A = A0.copy()
        for t in range(T):
            A = (1 - d) * (r * A + (1 - r) * (Pt @ A)); A[A < SUP] = 0; hit[k] |= A > 0
            if not A.any(): break
    for c in range(REP): hit[:, cues[c], c] = True   # cue nodes are not targets
    cnt = hit.sum(0)                                   # n x REP: combos activating each node
    noncue = np.ones((n, REP), bool)
    for c in range(REP): noncue[cues[c], c] = False
    v = cnt[noncue]
    edges = W.nnz // 2; diam = sp.csgraph.shortest_path(W > 0, unweighted=True, directed=False)
    return dict(net=path.split('/')[-1][:-4], n=n, edges=edges, diameter=int(diam[np.isfinite(diam)].max()),
                share_targets_all400=np.mean(v == 400), median_combos=np.median(v), min_combos=v.min(), share_targets_le380=np.mean(v <= 380))
if __name__ == '__main__':
    files = sorted(glob.glob('chen_nets/sim_*.csv')) + sorted(glob.glob('chen_nets/dist_*.csv'))
    with Pool(6) as p: out = pd.DataFrame(p.map(one, files))
    out['weights'] = out.net.str.split('_').str[0]; out.to_csv('chen_net_spread.csv', index=False)
    pd.set_option('display.width', 200)
    print('Combos (of 441) in which a non-cue node is activated at any step; r = 1 or d = 1 give 41 combos with no spread,')
    print('so 400 is the maximum possible for a target that is not a cue.')
    print(out.groupby('weights')[['n', 'edges', 'diameter', 'median_combos', 'min_combos', 'share_targets_all400', 'share_targets_le380']].agg(['median', 'min', 'max']).round(3).T.to_string())
