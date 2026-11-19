# Experiment 1 without S1_79, the participant Beucler & De Neys (2026, Sec. 2.3) excluded for concatenating cues
# (13 of 24 final responses contain cue words, e.g. TRUCKCAMP, BIRDFLU; logs/diag_concat.txt).
# Candidate sets and Chebyshev coefficients are kept identical to stan_s1_*_w.json (the formal simulation uses them).
import json
for kind in ['sum', 'prod']:
    d = json.load(open(f'stan_s1_{kind}_w.json')); keep = [i for i, s in enumerate(d['subjects']) if s != 'S1_79']
    assert len(keep) == d['N'] - 1
    d['yk'] = [d['yk'][i] for i in keep]; d['subjects'] = [d['subjects'][i] for i in keep]; d['N'] = len(keep)
    json.dump(d, open(f'stan_s1x_{kind}_w.json', 'w')); print(kind, 'N =', d['N'])
