# Describe the distinct success patterns of the Chen grid (which combos produce them, how many items they activate).
import numpy as np, pandas as pd
Z = np.load('chen_S.npz'); combos = Z['combos']
for rule in ['S_any', 'S_fin']:
    S = Z[rule]; keys = [tuple(s) for s in S]; df = pd.DataFrame(combos, columns=['r', 'd']); df['pat'] = [hash(k) for k in keys]; df['n_items'] = S.sum(1)
    print(f'\n{rule}:'); print(df.groupby('pat').agg(n_combos=('r', 'size'), n_items=('n_items', 'first'), r_range=('r', lambda v: f'{v.min()}-{v.max()}'), d_range=('d', lambda v: f'{v.min()}-{v.max()}')).sort_values('n_combos', ascending=False).to_string(index=False))
