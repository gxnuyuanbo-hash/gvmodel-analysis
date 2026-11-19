# Chen et al. (2026) person-level estimation on the 100 simulated datasets of the recovery pilot (04_参数还原):
# for each person pick the (r, d) whose success pattern best matches the person's correct/incorrect pattern
# (no answer counts as incorrect; missing trials skipped). Ties are common, so two tie rules are reported:
# Chen's own tie-breaker (greatest summed activation duration on items the model solves; main), centroid (mean r and d
# over all tied combos) and first-in-grid (like R which.max, r outer loop, d inner).
# Then compare with the true person breadth b and verification d, with observed accuracy, and with model D (person_XXX.csv).
import json, glob, numpy as np, pandas as pd
Z = np.load('chen_S.npz'); combos = Z['combos']; DUR = Z['dur']; R = '../04_参数还原/'
nsol = json.load(open('../03_真实数据/stan_s1_prod_w.json'))['nsol']
def chen(yk, S):
    obs = yk >= 0; corr = np.array([[1 <= yk[i, j] <= nsol[j] for j in range(yk.shape[1])] for i in range(yk.shape[0])])
    out = []
    for i in range(len(yk)):
        m = (S[:, obs[i]] == corr[i, obs[i]]).mean(1); best = np.flatnonzero(m == m.max())
        # Chen tie-breaker: greater summed activation duration on items solved by the model (over the person's items)
        sd = (DUR[best][:, obs[i]] * S[best][:, obs[i]]).sum(1); bc = best[np.argmax(sd)]
        out.append(dict(acc=corr[i, obs[i]].mean(), match=m.max(), nties=len(best), pattern=S[best[0]].sum(),
                        r_cen=combos[best, 0].mean(), d_cen=combos[best, 1].mean(), r_first=combos[best[0], 0], d_first=combos[best[0], 1], r_chen=combos[bc, 0], d_chen=combos[bc, 1]))
    return pd.DataFrame(out)
rows = []; allp = []
for rule in ['S_any', 'S_fin']:
    for f in sorted(glob.glob(R + 'data/sim_*.json')):
        k = f[-8:-5]; yk = np.array(json.load(open(f))['yk']); tr = json.load(open(R + f'data/truth_{k}.json'))
        c = chen(yk, Z[rule]); c['b_true'] = tr['b']; c['d_true'] = tr['d']
        D = pd.read_csv(R + f'out/person_{k}.csv'); c['b_D'] = D.b_mean.values; c['d_D'] = D.d_mean.values
        cc = lambda x, y: np.nan if c[x].std() == 0 or c[y].std() == 0 else np.corrcoef(c[x], c[y])[0, 1]
        rows.append(dict(rule=rule, ds=k, n_est_cen=c[['r_cen', 'd_cen']].drop_duplicates().shape[0], med_ties=c.nties.median(),
            **{f'{a}~{b}': cc(a, b) for a in ['r_chen', 'd_chen', 'r_cen', 'd_cen', 'r_first', 'd_first', 'acc', 'b_D'] for b in ['b_true', 'd_true']},
            **{'r_chen~acc': cc('r_chen', 'acc'), 'd_chen~acc': cc('d_chen', 'acc'), 'r_cen~acc': cc('r_cen', 'acc'), 'd_cen~acc': cc('d_cen', 'acc')}))
        c['rule'] = rule; c['ds'] = k; allp.append(c)
res = pd.DataFrame(rows); pd.concat(allp).to_csv('chen_person.csv', index=False); res.to_csv('chen_by_dataset.csv', index=False)
pd.set_option('display.width', 200)
for rule, g in res.groupby('rule'):
    print(f'\n=== success rule: {"activated at any step" if rule == "S_any" else "activated at step 100"} ===')
    print('distinct (r,d) estimates per dataset (centroid rule): median', g.n_est_cen.median(), '| median tied combos per person', g.med_ties.median())
    cols = [x for x in g.columns if '~' in x]
    print('median within-dataset correlation (NaN = estimate constant within dataset; n_nan shown):')
    print(pd.DataFrame({'median_r': g[cols].median().round(3), 'n_nan': g[cols].isna().sum()}).to_string())
