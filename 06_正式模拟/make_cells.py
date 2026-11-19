# Condition table for the formal simulation (design: 模拟设计_v0.1.md). Writes cells.json, read by every other script.
# study "s1": recovery and comparison, N x J x sigma (18 cells); "sbc": prior-matched SBC (key settings);
# "s3": careless responders at key settings. Study 2 (Chen home turf) needs no MCMC and is defined in sim_chen_home.py.
import json, itertools
cells = []
for c, (N, J, sg) in enumerate(itertools.product([50, 100, 200], [12, 24], [1.5, 2.5, 3.5])):
    key = (N, J, sg) == (100, 24, 2.5)
    cells.append(dict(study='s1', cell=c, N=N, J=J, sigma=sg, careless=None, prop=0.0, reps=1000 if key else 200, key=key))
cells.append(dict(study='sbc', cell=0, N=100, J=24, sigma=None, careless=None, prop=0.0, reps=1000, key=True))
for c, (typ, p) in enumerate(itertools.product(['random', 'giveup'], [.05, .10])):
    cells.append(dict(study='s3', cell=c, N=100, J=24, sigma=2.5, careless=typ, prop=p, reps=200, key=False))
json.dump(cells, open('cells.json', 'w'), indent=1)
print(len(cells), 'cells;', sum(x['reps'] for x in cells), 'fits in total')
