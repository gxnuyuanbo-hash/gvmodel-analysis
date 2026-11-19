# Model-free check for the two-stage analysis: how close to the cues are incorrect responses at stage a (initial, under
# time pressure and load) and stage b (final)? Valid trials only (to_exclude == 0), experiments 1 (without S1_79) and 2.
# Closeness of an incorrect word w to item j: number of cues c (0-3) with a direct SWOW-EN18 edge c -> w, and the summed
# transition probability sum_c P[c, w] (P row-normalized, as in the model). Paired comparison on trials incorrect at both stages.
# Output: logs/twostage_errors.txt
import json, numpy as np, pandas as pd, scipy.sparse as sp
z = np.load('Pt.npz'); Pt = sp.csr_matrix((z['data'], z['indices'], z['indptr']), shape=tuple(z['shape'])); P = Pt.T.tocsr()
nodes = json.load(open('nodes.json')); idx = {w: i for i, w in enumerate(nodes)}
it = pd.read_csv('../01_数据/gfsb8/Data/items_characteristics.csv', sep=';')
cues = [[idx[c] for c in it.problem[j].lower().split('/') if c in idx] for j in range(len(it))]
d = pd.read_csv('../01_数据/gfsb8/Data/two_response_CRAT_data.csv'); d['study'] = d.study.astype(str)
d = d[(d.study.isin(['1', '2'])) & (d.to_exclude == 0) & (d.subject != 'S1_79')].copy()
d['r'] = d.response.astype(str).str.lower().str.strip()
def close(row):
    w = idx.get(row.r); j = int(row.item_number) - 1
    if w is None: return pd.Series({'ncue': np.nan, 'pstr': np.nan})
    v = [P[c, w] for c in cues[j]]; return pd.Series({'ncue': sum(x > 0 for x in v), 'pstr': sum(v)})
e = d[d.response_type == 'Incorrect'].copy(); e[['ncue', 'pstr']] = e.apply(close, axis=1); e = e.dropna(subset=['ncue'])
out = ['Incorrect responses in the network, by stage (all valid trials):']
for (st, stg), g in e.groupby(['study', 'response_stage']):
    out.append(f'  exp {st} stage {stg}: n = {len(g)}, linked to >= 1 cue = {np.mean(g.ncue >= 1):.3f}, mean cues linked = {g.ncue.mean():.3f}, '
               f'mean summed P = {g.pstr.mean():.4f}, median = {g.pstr.median():.4f}')
w = e.pivot_table(index=['study', 'subject', 'item_number'], columns='response_stage', values=['ncue', 'pstr']).dropna()
same = e.pivot_table(index=['study', 'subject', 'item_number'], columns='response_stage', values='r', aggfunc='first').dropna()
out.append('Trials incorrect at both stages (paired):')
for st in ['1', '2']:
    ws = w.loc[st]; ss = same.loc[st]; changed = (ss.a != ss.b).mean()
    dn = ws[('ncue', 'b')] - ws[('ncue', 'a')]; dp = ws[('pstr', 'b')] - ws[('pstr', 'a')]
    out.append(f'  exp {st}: n = {len(ws)}, same word at both stages = {1 - changed:.3f}, mean change in cues linked (b - a) = {dn.mean():.3f}, '
               f'mean change in summed P = {dp.mean():.4f}; among changed words: cues linked change = {dn[(ss.a != ss.b).values].mean():.3f}')
open('logs/twostage_errors.txt', 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))
# paired bootstrap (resampling participants) for the change in cues linked and summed P on trials incorrect at both stages
rng = np.random.default_rng(20261120); out2 = ['Participant bootstrap (5,000), 95% CI of mean paired change b - a:']
for st in ['1', '2']:
    w0 = w.loc[st]; ws = pd.DataFrame({'dn': w0[('ncue', 'b')] - w0[('ncue', 'a')], 'dp': w0[('pstr', 'b')] - w0[('pstr', 'a')]}, index=w0.index)
    g = ws.groupby(level=0)[['dn', 'dp']].agg(['sum', 'count']); subs = g.index.values; bs = {'dn': [], 'dp': []}
    for _ in range(5000):
        s = rng.choice(len(subs), len(subs)); gg = g.iloc[s]
        for v in bs: bs[v].append(gg[(v, 'sum')].sum() / gg[(v, 'count')].sum())
    out2.append(f'  exp {st}: cues linked {np.mean(ws.dn):.3f} [{np.quantile(bs["dn"], .025):.3f}, {np.quantile(bs["dn"], .975):.3f}], '
                f'summed P {np.mean(ws.dp):.4f} [{np.quantile(bs["dp"], .025):.4f}, {np.quantile(bs["dp"], .975):.4f}]')
open('logs/twostage_errors.txt', 'a').write('\n'.join(out2) + '\n'); print('\n'.join(out2))
