# Diagnostic: rank of the solution among candidates under three cue-combination rules, across breadth.
# sum = joint spreading from all cues (activation.npz); product = sum_c log a_c; min = min_c log a_c (percue.npz).
import json, numpy as np, pandas as pd
g = np.load('activation.npz')['grid']; L = np.load('activation.npz')['logA'].astype(float); z = np.load('percue.npz')
nodes = json.load(open('nodes.json')); idx = {w: i for i, w in enumerate(nodes)}; cands = json.load(open('candidates.json'))
it = pd.read_csv('../01_数据/gfsb8/Data/items_characteristics.csv', sep=';')
rules = {'sum': lambda j: np.array([L[j][idx[w]] for w in cands[j]]), 'product': lambda j: z[str(j)].sum(0), 'min': lambda j: z[str(j)].min(0)}
for name, f in rules.items():
    for gi in [0, 10, 20, 30, 40]:
        ranks = []
        for j, c in enumerate(cands):
            S = f(j); sols = [c.index(w) for w in it.solution[j].lower().split('/')]
            best = max(S[k, gi] for k in sols); ranks.append(int((S[:, gi] > best).sum()) + 1)
        print(f'{name:8s} logit {g[gi]:5.1f}  median rank {np.median(ranks):5.1f}  top1 {sum(r == 1 for r in ranks):2d}/24  top3 {sum(r <= 3 for r in ranks):2d}/24')
