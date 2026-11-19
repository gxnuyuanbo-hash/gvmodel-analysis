# Per-cue activation (each cue spreads alone); stores log a_c(theta) for candidate words only.
import sys, csv, json, numpy as np, pandas as pd, scipy.sparse as sp
D = sys.argv[1]; T = 1500
s = pd.read_csv(D + '/SWOW-EN18/unzipped/strength.SWOW-EN.R123.20180827.csv', sep='\t', quoting=csv.QUOTE_NONE, keep_default_na=False)
s['cue'] = s.cue.str.lower().str.strip(); s['response'] = s.response.str.lower().str.strip()
it = pd.read_csv(D + '/gfsb8/Data/items_characteristics.csv', sep=';')
nodes = json.load(open('nodes.json')); idx = {w: i for i, w in enumerate(nodes)}; n = len(nodes)
s = s[s.response.isin(idx) & s.cue.isin(idx) & (s.cue != s.response)]
s = s.groupby(['cue', 'response'], as_index=False)['R123.Strength'].sum()
W = sp.csr_matrix((s['R123.Strength'].values, (s.cue.map(idx).values, s.response.map(idx).values)), shape=(n, n))
W = (W + W.T) / 2; deg = np.asarray(W.sum(1)).ravel()
Pt = (sp.diags(1 / deg) @ W).T.tocsr()
grid = np.load('activation.npz')['grid']; th = 1 / (1 + np.exp(-grid))
cands = json.load(open('candidates.json')); out = {}
for j, p in enumerate(it.problem):
    ci = [idx[w] for w in cands[j]]; res = []
    for c in p.lower().split('/'):
        v = np.zeros(n); v[idx[c]] = 1; acc = np.zeros((len(ci), len(grid))); pw = np.ones(len(grid))
        for t in range(T):
            acc += np.outer(v[ci], pw); v = Pt @ v; pw = pw * th
        res.append(np.log(np.maximum(acc * (1 - th), 1e-300)))
    out[str(j)] = np.array(res)  # 3 x K_j x G
    print(j, flush=True)
np.savez_compressed('percue.npz', **out)
