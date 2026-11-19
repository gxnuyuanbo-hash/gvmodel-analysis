# Connectivity and mixing rate of the random walk on the SWOW network.
# If connected and aperiodic, a0 = c*pi + r with sum(r)=0 and (P^T)^t r decays at the rate of the 2nd eigenvalue,
# which allows exact activation at breadth close to 1 via a(theta) = c*pi + (1-theta) sum_t theta^t (P^T)^t r.
import csv, json, numpy as np, pandas as pd, scipy.sparse as sp, scipy.sparse.csgraph as cg
nodes = json.load(open('nodes.json')); idx = {w: i for i, w in enumerate(nodes)}; n = len(nodes)
s = pd.read_csv('../01_数据/SWOW-EN18/unzipped/strength.SWOW-EN.R123.20180827.csv', sep='\t', quoting=csv.QUOTE_NONE, keep_default_na=False)
s['cue'] = s.cue.str.lower().str.strip(); s['response'] = s.response.str.lower().str.strip()
s = s[s.response.isin(idx) & s.cue.isin(idx) & (s.cue != s.response)].groupby(['cue', 'response'], as_index=False)['R123.Strength'].sum()
W = sp.csr_matrix((s['R123.Strength'].values, (s.cue.map(idx).values, s.response.map(idx).values)), shape=(n, n)); W = (W + W.T) / 2
ncomp, lab = cg.connected_components(W, directed=False); print('components', ncomp, 'largest', np.bincount(lab).max())
deg = np.asarray(W.sum(1)).ravel(); pi = deg / deg.sum(); Pt = (sp.diags(1 / deg) @ W).T.tocsr()
v = np.zeros(n); v[idx['fire']] = 1; r = v - pi
for t in range(0, 401):
    if t in (0, 5, 10, 20, 50, 100, 200, 400): print(t, '%.2e' % np.abs(r).sum())
    r = Pt @ r
sp.save_npz('Pt.npz', Pt); np.save('pi.npy', pi)
