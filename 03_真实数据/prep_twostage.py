# Two-stage analysis (Beucler & De Neys, 2026, two-response paradigm): stage a = initial response under time pressure and
# cognitive load, stage b = final response. For experiments 1 (without S1_79) and 2, build Stan data for
#   <smp>a  : stage-a responses on valid trials (to_exclude == 0: load task correct and response within the deadline)
#   <smp>bm : stage-b responses on the same valid trials (matched comparison)
# Candidate sets, K and Chebyshev coefficients are taken unchanged from stan_<smp>_prod_w.json, so the two stages are
# scored on identical candidate sets. Output: stan_<smp>{a,bm}_prod_w.json; summary in logs/prep_twostage.txt
import json, pandas as pd
d = pd.read_csv('../01_数据/gfsb8/Data/two_response_CRAT_data.csv'); d['study'] = d.study.astype(str)
d['r'] = d.response.astype(str).str.lower().str.strip()
cands = json.load(open('candidates.json')); out = []
for smp, st in [('s1x', '1'), ('s2', '2')]:
    base = json.load(open(f'stan_{smp}_prod_w.json')); subs = base['subjects']; sid = {s: i for i, s in enumerate(subs)}; nsol = base['nsol']
    for tag, stage in [('a', 'a'), ('bm', 'b')]:
        q = d[(d.study == st) & (d.response_stage == stage) & (d.to_exclude == 0) & d.subject.isin(subs)]
        yk = [[-1] * base['J'] for _ in subs]; dropped = 0
        for _, row in q.iterrows():
            j = int(row.item_number) - 1
            if row.response_type == 'No_answer' or pd.isna(row.response): k = 0
            elif row.r in cands[j]: k = cands[j].index(row.r) + 1
            else: dropped += 1; continue
            yk[sid[row.subject]][j] = k
        obs = [k for row in yk for k in row if k >= 0]
        acc = sum(1 for i, row in enumerate(yk) for j, k in enumerate(row) if 1 <= k <= nsol[j]) / len(obs)
        noans = sum(1 for k in obs if k == 0) / len(obs)
        nd = dict(base); nd['yk'] = yk; json.dump(nd, open(f'stan_{smp}{tag}_prod_w.json', 'w'))
        out.append(f'{smp}{tag}: N = {len(subs)}, valid trials = {len(q)}, coded = {len(obs)}, not in candidates = {dropped}, accuracy = {acc:.3f}, no answer = {noans:.3f}')
open('logs/prep_twostage.txt', 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))
