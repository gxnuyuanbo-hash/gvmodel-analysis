# Add solution indicator vector `sol` (1 for solution slots) to *_prod data -> *_prod_v (used by breadth_verify.stan).
import json, sys
for s in sys.argv[1:]:
    d = json.load(open(f'stan_{s}_prod.json')); K = d['K']; sol = [0.0] * (d['J'] * K)
    for j, n in enumerate(d['nsol']):
        for k in range(n): sol[j * K + k] = 1.0
    d['sol'] = sol; json.dump(d, open(f'stan_{s}_prod_v.json', 'w'))
