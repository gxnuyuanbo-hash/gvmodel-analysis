# Candidate sets, response coding, Chebyshev coefficients for each sample.
import sys, json, numpy as np, pandas as pd
D = sys.argv[1]; NC = int(sys.argv[2]) if len(sys.argv) > 2 else 12; TOP = 20
z = np.load('activation.npz'); logA = z['logA'].astype(float); grid = z['grid']
nodes = json.load(open('nodes.json')); idx = {w: i for i, w in enumerate(nodes)}
it = pd.read_csv(D + '/gfsb8/Data/items_characteristics.csv', sep=';')
d = pd.read_csv(D + '/gfsb8/Data/two_response_CRAT_data.csv')
d['study'] = d.study.astype(str); d['r'] = d.response.astype(str).str.lower().str.strip()
J = len(it); mid = len(grid) // 2
lo, hi = grid[0], grid[-1]; x = (2 * grid - lo - hi) / (hi - lo)
B = np.polynomial.chebyshev.chebvander(x, NC - 1)       # G x NC
cands = []
for j in range(J):
    sols = it.solution[j].lower().split('/'); cues = it.problem[j].lower().split('/')
    obs = d[(d.item_number == j + 1) & (d.response_type != 'No_answer') & d.response.notna()].r
    c = list(dict.fromkeys(sols + [w for w in obs if w in idx and w not in sols]))
    order = np.argsort(-logA[j][:, mid])
    for k in order:
        if len([1 for _ in c]) >= len(c) and sum(1 for w in c if w not in sols and w not in obs.values) >= TOP: break
        w = nodes[k]
        if w not in c and w not in cues: c.append(w)
    cands.append(c)
K = max(len(c) for c in cands); print('K per item', [len(c) for c in cands], 'Kmax', K)
C = np.zeros((J * K, NC)); pad = np.full(J * K, -1e4); maxerr = 0
for j, c in enumerate(cands):
    for k, w in enumerate(c):
        y = logA[j][idx[w]]; coef, *_ = np.linalg.lstsq(B, y, rcond=None)
        maxerr = max(maxerr, np.abs(B @ coef - y).max())
        C[j * K + k] = coef; pad[j * K + k] = 0
print('Chebyshev', NC, 'terms, max abs error on grid', round(maxerr, 4))
xf = (2 * np.linspace(lo, hi, 401) - lo - hi) / (hi - lo)
samples = {'s1': ('1', 'b'), 's2': ('2', 'b'), 'pre': ('one_resp_pre_test', None)}
summary = {}
for name, (st, stage) in samples.items():
    q = d[d.study == st] if stage is None else d[(d.study == st) & (d.response_stage == stage)]
    subs = sorted(q.subject.unique()); N = len(subs); sid = {s: i for i, s in enumerate(subs)}
    yk = np.full((N, J), -1, int); dropped = 0
    for _, row in q.iterrows():
        j = int(row.item_number) - 1
        if row.response_type == 'No_answer' or pd.isna(row.response): k = 0
        elif row.r in cands[j]: k = cands[j].index(row.r) + 1
        else: dropped += 1; continue
        yk[sid[row.subject], j] = k
    keep = ~(yk < 0).all(1)   # exclusion: participants with no mappable response (e.g., pretest_36 typed the joined cues)
    excl = [s for s, k in zip(subs, keep) if not k]; yk = yk[keep]; subs = [s for s, k in zip(subs, keep) if k]; N = len(subs)
    nsol = [len(it.solution[j].split('/')) for j in range(J)]
    corr = [[1 if 1 <= yk[i, j] <= nsol[j] else 0 for j in range(J)] for i in range(N)]
    summary[name] = dict(N=N, excluded=excl, dropped=dropped, missing=int((yk < 0).sum()))
    json.dump(dict(N=N, J=J, K=K, D=NC, lo=lo, hi=hi, C=C.tolist(), pad=pad.tolist(), yk=yk.tolist(),
                   nsol=nsol, subjects=subs), open(f'stan_{name}.json', 'w'))
print(summary)
json.dump(cands, open('candidates.json', 'w'))
