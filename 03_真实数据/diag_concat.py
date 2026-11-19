# Find participants whose final responses contain cue words (e.g. "basketfootvolley", "basket" for basket/foot/volley),
# the pattern Beucler & De Neys (2026, Sec. 2.3) used to exclude one Experiment-1 participant (and our pretest_36).
import pandas as pd, sys
d = pd.read_csv('../01_数据/gfsb8/Data/two_response_CRAT_data.csv', sep=None, engine='python')
d = d[d.response_stage.astype(str).str.lower().str.contains('b|final')] if d.response_stage.astype(str).str.contains('b').any() else d
def cueuse(r):
    resp = str(r.response).lower().replace(' ', ''); cues = str(r.problem).lower().split('/')
    return any(c in resp for c in cues) and resp not in ('', 'nan')
d['cue_in_resp'] = d.apply(cueuse, axis=1)
s = d.groupby(['study', 'subject']).agg(n=('cue_in_resp', 'size'), cue=('cue_in_resp', 'sum')).reset_index()
s['share'] = s.cue / s.n
print(s.sort_values('share', ascending=False).head(8).to_string(index=False))
top = s.sort_values('share', ascending=False).iloc[0]
print('\nresponses of top subject:', d[(d.study == top.study) & (d.subject == top.subject)][['problem', 'response']].head(8).to_string(index=False))
