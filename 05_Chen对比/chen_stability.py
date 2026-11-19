# Chen et al.'s stability check applied to our simulated data: resample 90% of items 1,000 times, re-run grid matching,
# and record for each person the proportion of resamples that return the same (r, d) as the full-item estimate
# (Chen report median .68 on all items). Tie rule: Chen's duration tie-breaker. Stability as Chen define it: share of
# resamples in which the modal pair reappears; also solution diversity (number of distinct pairs). Rule: S_any.
# Point: in our simulated data the true process has no r or d, so any "stability" here is stability of an accuracy proxy.
import json, glob, numpy as np, pandas as pd
Z = np.load('chen_S.npz'); S = Z['S_any'].astype(float); combos = Z['combos']; DUR = Z['dur'] * Z['S_any']; R = '../04_参数还原/'
nsol = json.load(open('../03_真实数据/stan_s1_prod_w.json'))['nsol']; J = S.shape[1]; rng = np.random.default_rng(20261111); B = 1000
out = []
for f in sorted(glob.glob(R + 'data/sim_*.json')):
    yk = np.array(json.load(open(f))['yk']); obs = (yk >= 0).astype(float)
    corr = np.array([[1 <= yk[i, j] <= nsol[j] for j in range(J)] for i in range(len(yk))], float)
    def est(w):  # w: item weights (0/1); returns index of first best combo per person
        agree = (corr * obs * w) @ S.T + ((1 - corr) * obs * w) @ (1 - S).T; n = (obs * w).sum(1, keepdims=True)
        acc = agree / n; best = np.isclose(acc, acc.max(1, keepdims=True))
        tb = (obs * w) @ DUR.T                                  # Chen tie-breaker: summed duration on items the model solves
        return np.argmax(np.where(best, tb, -1), 1)
    full = est(np.ones(J)); boot = np.zeros((B, len(yk)), int)
    for b in range(B):
        w = np.zeros(J); w[rng.choice(J, int(round(.9 * J)), replace=False)] = 1; boot[b] = est(w)
    modal = np.array([np.bincount(boot[:, i]).argmax() for i in range(len(yk))])
    out.append(pd.DataFrame(dict(ds=f[-8:-5], repro=(boot == full).mean(0), modal_prop=(boot == modal).mean(0),
                                 diversity=[len(set(boot[:, i])) for i in range(len(yk))], combo=full)))
d = pd.concat(out); d.to_csv('chen_stability.csv', index=False)
print('Chen stability proportion (share of resamples returning the modal pair): median', round(d.modal_prop.median(), 3), '| mean', round(d.modal_prop.mean(), 3))
print('share returning the full-item pair: median', round(d.repro.median(), 3), '| solution diversity: median', d.diversity.median())
print('share of persons whose full-item estimate is one of the 2 extreme patterns (all items / no items):',
      round(np.isin(d.combo, np.flatnonzero(S.sum(1) == J) ).mean() + np.isin(d.combo, np.flatnonzero(S.sum(1) == 0)).mean(), 3))
print('number of distinct full-item estimates per dataset: median', d.groupby('ds').combo.nunique().median())
