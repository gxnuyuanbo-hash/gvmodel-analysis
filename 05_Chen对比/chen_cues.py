# Recover each Chen item's 3 cue words: the free-association file lists the cue in row 1 (one column per participant-response),
# 240 cues = 80 items x 3. Check against the item networks: are the first 3 nodes of wu_k the cues, in the same order?
# Output: chen_cues.csv (item, cue1..3, cue positions in the network), logs/chen_cues.txt
import openpyxl, pandas as pd
F = '../01_数据/Chen2026_自由联想/RawData_ModifiedFreeAssociationTask.xlsx'; B = '../01_数据/Chen2026_网络/unzipped/path_wu/'
ws = openpyxl.load_workbook(F, read_only=True).active; row1 = next(ws.iter_rows(max_row=1, values_only=True))
cues = []
for c in row1:
    c = str(c).strip() if c is not None else None
    if c and (not cues or cues[-1] != c): cues.append(c)
print('distinct cue runs in row 1:', len(cues), '| unique cues:', len(set(cues)))
rows = []
for k in range(80):
    h = [str(x).strip() for x in next(openpyxl.load_workbook(B + f'wu_{k}.xlsx', read_only=True).active.iter_rows(max_row=1, values_only=True))[1:]]
    first3 = h[:3]; pos = {c: (h.index(c) if c in h else -1) for c in cues}
    rows.append(dict(item=k, n_nodes=len(h), first3='/'.join(first3), cues_in_fa_order='/'.join(cues[3 * k:3 * k + 3]) if len(cues) >= 3 * k + 3 else '',
                     first3_are_fa_cues=set(first3) == set(cues[3 * k:3 * k + 3])))
d = pd.DataFrame(rows); d.to_csv('chen_cues.csv', index=False)
print('items where the first 3 network nodes equal the 3 consecutive free-association cues:', d.first3_are_fa_cues.sum(), 'of 80')
print(d.head(12).to_string(index=False))
