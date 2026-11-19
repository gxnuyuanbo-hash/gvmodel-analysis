# Chen et al. (2026) person-level estimation on every simulated dataset of one cell, with their own rules:
# success = solution activated (> 0) at any step (spreadr, initial 30, 100 steps, suppress .001; grid from 05_Chen对比/chen_S.npz);
# best pair = max share of items where person correctness matches model success; ties broken by the greater summed activation
# duration on items the model solves; stability = 1,000 resamples of 90% of items, share of resamples returning the modal pair,
# persons with < 10 usable items in a resample are skipped for that resample. No answer counts as incorrect; missing skipped.
# Usage: python3 -I chen_apply.py <study> <cell>   ->  out/<study>/c<cell>/chen_<rep>.csv (skips existing)
import json, glob, os, sys, numpy as np, pandas as pd
study, cell = sys.argv[1], int(sys.argv[2]); B = 1000
Z = np.load('../05_Chen对比/chen_S.npz'); S_all = Z['S_any'].astype(float); DUR_all = Z['dur'] * Z['S_any']; combos = Z['combos']
od = f'out/{study}/c{cell:02d}'; os.makedirs(od, exist_ok=True)
def est(corr, obs, w, S, DUR):
    use = obs * w; n = use.sum(1, keepdims=True)
    agree = (corr * use) @ S.T + ((1 - corr) * use) @ (1 - S).T
    acc = agree / np.maximum(n, 1); best = np.isclose(acc, acc.max(1, keepdims=True))
    pick = np.argmax(np.where(best, use @ DUR.T, -1), 1)
    return np.where(n[:, 0] >= 10, pick, -1)
for f in sorted(glob.glob(f'data/{study}/c{cell:02d}/sim_*.json')):
    rep = f[-9:-5]; outf = f'{od}/chen_{rep}.csv'
    if os.path.exists(outf): continue
    d = json.load(open(f)); yk = np.array(d['yk']); items = np.array(d['items']); nsol = np.array(d['nsol']); J = len(items)
    S, DUR = S_all[:, items], DUR_all[:, items]; obs = (yk >= 0).astype(float)
    corr = ((yk >= 1) & (yk <= nsol[None, :])).astype(float)
    full = est(corr, obs, np.ones(J), S, DUR)
    rng = np.random.default_rng(np.random.SeedSequence([99, cell, int(rep)])); boot = np.empty((B, len(yk)), int)
    for b in range(B):
        w = np.zeros(J); w[rng.choice(J, int(round(.9 * J)), replace=False)] = 1; boot[b] = est(corr, obs, w, S, DUR)
    modal, prop, div = [], [], []
    for i in range(len(yk)):
        v = boot[:, i][boot[:, i] >= 0]
        if len(v) == 0: modal.append(-1); prop.append(np.nan); div.append(0); continue
        mo = np.bincount(v).argmax(); modal.append(mo); prop.append((v == mo).mean()); div.append(len(set(v)))
    ok = full >= 0
    pd.DataFrame(dict(rep=rep, person=np.arange(1, len(yk) + 1), acc=(corr * obs).sum(1) / np.maximum(obs.sum(1), 1),
                      r_chen=np.where(ok, combos[full, 0], np.nan), d_chen=np.where(ok, combos[full, 1], np.nan),
                      stability=prop, diversity=div)).to_csv(outf, index=False)
