# Build the English Supplementary Material (markdown) from supp/S1_proofs_en.md and the CSV tables written by
# tables_supp.R. Usage (from 07_论文/): python3 -I scripts/supp_en.py   Output: supp/Supplementary_Material_en.md
# Section S1: proofs of the three properties of spreadr grid matching; Tables S1–S3: Simulation 3 (careless
# responders; supp/S2*.csv); Tables S4–S6: Simulation 1, all 18 cells (supp/S3*.csv).
import csv
C = {'随机作答 5%': 'Random 5%', '随机作答 10%': 'Random 10%', '放弃作答 5%': 'Give-up 5%', '放弃作答 10%': 'Give-up 10%',
     '无粗心作答（关键格）': 'No careless responders (key cell)'}
PV = ['mu', 'sigma', 'gamma', 'kappa', 'delta', 'tau', 'rho']; G = dict(zip(PV, 'μσγκδτρ'))
def rd(f): return list(csv.DictReader(open('supp/' + f, encoding='utf-8')))
def f2(x, d=2):
    if x in ('', 'NA', None): return '—'
    v = float(x); s = f'{v:.{d}f}'.replace('-', '−'); return s.replace('0.', '.', 1) if abs(v) < 1 and s.lstrip('−').startswith('0.') else s
def fb(x): v = float(x); s = f'{v:.2f}'; return ('0.00' if s in ('-0.00', '0.00') else s.replace('-', '−'))   # bias, unbounded: keep leading zero
def table(num, title, head, rows, note):
    out = [f'**Table {num}. {title}**', '', '| ' + ' | '.join(head) + ' |', '|' + '---|' * len(head)]
    out += ['| ' + ' | '.join(r) + ' |' for r in rows]; return out + ['', f'*Note.* {note}', '']
md = ['# Supplementary Material', '',
      'Estimating spreading-activation breadth and verification ability from remote associates responses: A generation–verification model', '']
md += open('supp/S1_proofs_en.md', encoding='utf-8').read().strip().split('\n') + ['']
# ---------------- S2: Simulation 3
a = rd('S2a_population_long.csv'); conds = list(dict.fromkeys(r['cond'] for r in a))
rows = [[C[c]] + [f"{fb(r['bias'])} ({f2(r['cover90'])})" for p in PV for r in a if r['cond'] == c and r['variable'] == p] for c in conds]
md += table('S1', 'Simulation 3 (careless responders): bias (90% coverage) of the population parameters', ['Condition'] + [G[p] for p in PV], rows,
            'Each condition has 200 data sets with *N* = 100, *J* = 24, σ = 2.5; the first row is the key cell of Simulation 1 (1,000 data sets). '
            'Random responders choose uniformly among no answer and all candidates on each item; give-up responders give no answer with probability .9 '
            'on each item and otherwise respond according to the model. True population parameters are those of the careful responders. Bias = posterior mean − true value.')
b = rd('S2b_person_by_group.csv')
rows = [[C[r['cond']], 'Careless' if r['careless'] == 'TRUE' else 'Careful', f"{int(r['n']):,}", fb(r['b_true']), fb(r['b_mean']), fb(r['b_bias']), f2(r['cover_b']),
         fb(r['d_true']), fb(r['d_mean']), fb(r['d_bias']), f2(r['cover_d']), f2(r['r_b']), f2(r['r_d']), f2(r['pct_b']), f2(r['extreme'])] for r in b]
md += table('S2', 'Simulation 3: person parameters of careful and careless responders',
            ['Condition', 'Group', '*n*', 'True *b*', 'Est. *b*', 'Bias *b*', 'Cov. *b*', 'True *v*', 'Est. *v*', 'Bias *v*', 'Cov. *v*', '*r*(*b*)', '*r*(*v*)', 'Pct. *b*', 'Det.'], rows,
            'True values of careless responders are drawn from the same population but do not generate their responses, so their bias and coverage show where the estimates are pushed. '
            '*r*(*b*) and *r*(*v*) are computed for careful responders only (median within-data-set correlation). Pct. *b*: mean percentile of careless responders\' posterior breadth among all participants of the data set. '
            '*n*: number of persons. Det.: with *k* careless responders in a data set, the share of careless responders among the *k* participants with the highest (random) or lowest (give-up) posterior breadth.')
c = rd('S2c_gridmatching.csv')
rows = [[C[r['cond']], f2(r['r_chen_b']), f2(r['d_chen_b']), f2(r['r_chen_acc']), f2(r['d_chen_acc']), f2(r['D_b']), f2(r['stab']), r['n_est']] for r in c]
md += table('S3', 'Simulation 3: grid matching with careless responders',
            ['Condition', '*r*(*r̂*, *b*)', '*r*(*d̂*, *b*)', '*r*(*r̂*, acc.)', '*r*(*d̂*, acc.)', 'G–V model *r*(*b*)', 'Stability', 'Distinct estimates'], rows,
            'Careful responders only; median within-data-set correlations. *r̂*, *d̂*: grid-matching estimates; acc.: accuracy; G–V: generation–verification model.')
# ---------------- S3: Simulation 1
a = rd('S3a_population_long.csv'); cells = list(dict.fromkeys(r['cell'] for r in a)); lab = {r['cell']: (r['N'], r['J'], r['sigma']) for r in a}
rows = [list(lab[cl]) + [f"{fb(r['bias'])} ({f2(r['cover90'])})" for p in PV for r in a if r['cell'] == cl and r['variable'] == p] for cl in cells]
rows.sort(key=lambda r: (int(r[0]), int(r[1]), float(r[2])))
md += table('S4', 'Simulation 1, all 18 cells: bias (90% coverage) of the population parameters', ['*N*', '*J*', 'σ'] + [G[p] for p in PV], rows,
            '200 data sets per cell (1,000 in the key cell, *N* = 100, *J* = 24, σ = 2.5). Bias = posterior mean − true value. RMSE and interval widths are in `S3a_population_long.csv` of the analysis repository.')
b = rd('S3b_person.csv'); b.sort(key=lambda r: (int(r['N']), int(r['J']), float(r['sigma'])))
rows = [[r['N'], r['J'], r['sigma'], f2(r['r_b']), f2(r['r_d']), f2(r['cover_b']), f2(r['cover_d']), f2(r['err_bd']), f2(r['< -4']), f2(r['-4..-1']), f2(r['-1..2']), f2(r['> 2'])] for r in b]
md += table('S5', 'Simulation 1, all 18 cells: recovery of person parameters',
            ['*N*', '*J*', 'σ', '*r*(*b*)', '*r*(*v*)', 'Cov. *b*', 'Cov. *v*', 'Error *r*', '*b* < −4', '−4 ≤ *b* < −1', '−1 ≤ *b* < 2', '*b* ≥ 2'], rows,
            '*r*(*b*), *r*(*v*): median within-data-set correlation between true values and posterior means. Error *r*: correlation of the estimation errors of *b* and *v*. '
            'The last four columns give the 90% coverage of *b* by true-breadth zone.')
c = rd('S3c_gridmatching_convergence.csv'); c.sort(key=lambda r: (int(r['N']), int(r['J']), float(r['sigma'])))
rows = [[r['N'], r['J'], r['sigma'], f2(r['r_chen_b']), f2(r['d_chen_b']), f2(r['r_chen_acc']), f2(r['d_chen_acc']), f2(r['stab']), r['n_est'], f"{int(r['n_rep']):,}",
         f2(r['converged']), f2(r['refitted']), f"{float(r['time_min']):.1f}"] for r in c]
md += table('S6', 'Simulation 1, all 18 cells: grid-matching estimates and convergence of the generation–verification model',
            ['*N*', '*J*', 'σ', '*r*(*r̂*, *b*)', '*r*(*d̂*, *b*)', '*r*(*r̂*, acc.)', '*r*(*d̂*, acc.)', 'Stability', 'Distinct estimates', 'Data sets', 'Conv.', 'Refitted', 'Time (min)'], rows,
            '*r̂*, *d̂*: grid-matching estimates on the same data. Stability: grid-matching stability index (median over data sets). Distinct estimates: median number of distinct (*r̂*, *d̂*) pairs in a data set. '
            'Conv.: share of data sets with R̂ ≤ 1.01, bulk and tail ESS ≥ 400, and no divergent transitions after the refit rule. Time: median fitting time per data set.')
open('supp/Supplementary_Material_en.md', 'w', encoding='utf-8').write('\n'.join(md) + '\n'); print('written supp/Supplementary_Material_en.md')
