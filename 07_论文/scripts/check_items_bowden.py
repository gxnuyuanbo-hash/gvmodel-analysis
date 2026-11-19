# Check which of the 24 gfsb8 CRA items appear verbatim (cue triple, any order) in Bowden & Jung-Beeman (2003)'s 144-item table.
# Usage: python3 -I check_items_bowden.py <items_characteristics.csv> <bowden_text.txt>
import sys, re, itertools, pandas as pd
it = pd.read_csv(sys.argv[1], sep=';'); t = re.sub(r'\s+', ' ', open(sys.argv[2]).read().lower())
rows = []
for _, r in it.iterrows():
    cues = r['problem'].lower().split('/'); found = None
    for p in itertools.permutations(cues):
        m = re.search(r'\b' + r'\s*/\s*'.join(map(re.escape, p)) + r'\b\s+(\w+)', t)
        if m: found = (p, m.group(1)); break
    near = None
    if not found:   # same solution with two of three cues -> variant of a Bowden item
        for m in re.finditer(r'([a-z]+)\s*/\s*([a-z]+)\s*/\s*([a-z]+)\s+' + re.escape(str(r['solution']).lower().split('/')[0]) + r'\b', t):
            if len(set(m.groups()) & set(cues)) >= 1: near = '/'.join(m.groups())
    rows.append(dict(item=r['problem'], solution=r['solution'], difficulty=r['difficulty'], in_bowden=bool(found),
                     bowden_solution=found[1] if found else '', bowden_variant=near or ''))
d = pd.DataFrame(rows); print(d.to_string(index=False)); print('\nverbatim in Bowden & Jung-Beeman (2003):', d.in_bowden.sum(), 'of', len(d))
