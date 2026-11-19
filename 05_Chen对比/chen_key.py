# Parse the CWRAT item table (cues and reference answers) from the appendix of 陈静、许天委、陈群林 (2024), 心理技术与应用 12(5),
# and match it to Chen et al.'s 80 item networks (wu_<id-1>). Answer node: exact match in the network, else not present.
# Cues used in the simulation are the network's first 3 nodes (what Chen et al. activated); some differ from the published
# table (shortened forms such as 花 for 花朵, or replaced cues in revised items), which is reported here.
# Usage: python3 -I chen_key.py <paper_text.txt>   Output: chen_key.csv, logs/chen_key.txt
import sys, re, openpyxl, pandas as pd
t = open(sys.argv[1]).read(); a = t[t.index('附录'):]; a = a[a.index('参考答案') + 4:]   # parse only the appendix table
tok = re.sub(r'\s+', ' ', a).split(' ')
rows, i = [], 0
while i + 4 < len(tok) and len(rows) < 80:
    if tok[i].isdigit() and int(tok[i]) == len(rows) + 1:
        rows.append(dict(id=int(tok[i]), cue1=tok[i + 1], cue2=tok[i + 2], cue3=tok[i + 3], answer=tok[i + 4])); i += 5
    else: i += 1
key = pd.DataFrame(rows); print('items parsed:', len(key))
B = '../01_数据/Chen2026_网络/unzipped/path_wu/'; out = []
for _, r in key.iterrows():
    h = [str(x).strip() for x in next(openpyxl.load_workbook(B + f'wu_{r.id - 1}.xlsx', read_only=True).active.iter_rows(max_row=1, values_only=True))[1:]]
    cues = [r.cue1, r.cue2, r.cue3]
    out.append(dict(**r, net_first3='/'.join(h[:3]), cues_match=sum(c in h[:3] for c in cues), answer_in_net=r.answer in h,
                    answer_idx=h.index(r.answer) if r.answer in h else -1))
d = pd.DataFrame(out); d.to_csv('chen_key.csv', index=False)
print('cue words found among the first 3 network nodes: 3/3 for', (d.cues_match == 3).sum(), 'items')
print('answer present as a node in the item network:', d.answer_in_net.sum(), 'of', len(d), '(Chen et al. kept 69 items after also dropping pass rate < .10)')
print(d.head(10).to_string(index=False)); print('\nitems with cue mismatch:'); print(d[d.cues_match < 3][['id', 'cue1', 'cue2', 'cue3', 'net_first3']].to_string(index=False))
