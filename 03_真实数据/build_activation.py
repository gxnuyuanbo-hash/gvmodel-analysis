# Build SWOW-EN18 network and per-item activation series for gfsb8 CRA items.
# Network: nodes = SWOW cues + item words missing as cues; symmetric weights (W + W^T)/2 on R123 strength,
# restricted to responses that are nodes. P = row-normalized. Activation a(theta) = (1-theta) sum_t theta^t (P^T)^t a0.
import sys, csv, json, numpy as np, pandas as pd, scipy.sparse as sp
D = sys.argv[1]; T = 1500
s = pd.read_csv(D + '/SWOW-EN18/unzipped/strength.SWOW-EN.R123.20180827.csv', sep='\t',
                quoting=csv.QUOTE_NONE, keep_default_na=False)
s['cue'] = s.cue.str.lower().str.strip(); s['response'] = s.response.str.lower().str.strip()
it = pd.read_csv(D + '/gfsb8/Data/items_characteristics.csv', sep=';')
itemwords = set()
for p, sol in zip(it.problem, it.solution): itemwords |= set(p.lower().split('/')) | set(sol.lower().split('/'))
nodes = sorted(set(s.cue) | itemwords)
idx = {w: i for i, w in enumerate(nodes)}; n = len(nodes)
s = s[s.response.isin(idx) & (s.cue != s.response)]
s = s.groupby(['cue', 'response'], as_index=False)['R123.Strength'].sum()
W = sp.csr_matrix((s['R123.Strength'].values, (s.cue.map(idx).values, s.response.map(idx).values)), shape=(n, n))
W = (W + W.T) / 2
deg = np.asarray(W.sum(1)).ravel()
print('nodes', n, 'nnz', W.nnz, 'isolated', int((deg == 0).sum()))
Pt = (sp.diags(1 / np.where(deg > 0, deg, 1)) @ W).T.tocsr()
grid = np.linspace(-5, 5, 41); th = 1 / (1 + np.exp(-grid))
logA = []  # per item: n x G log activation
for p in it.problem:
    a0 = np.zeros(n); cs = [idx[c] for c in p.lower().split('/')]; a0[cs] = 1 / 3
    acc = np.zeros((n, len(grid))); v = a0.copy(); pw = np.ones(len(grid))
    for t in range(T):
        acc += np.outer(v, pw); v = Pt @ v; pw = pw * th
    A = acc * (1 - th)
    logA.append(np.log(np.maximum(A, 1e-300)))
    print(p, 'tail weight at max theta', round(float(th[-1] ** T), 6), flush=True)
np.savez_compressed('activation.npz', logA=np.array(logA, dtype=np.float32), grid=grid, deg=deg)
json.dump(nodes, open('nodes.json', 'w'))
