# Convert the manuscript markdown to APA 7 / Behavior Research Methods Word files.
# Usage (from 07_论文/): python3 -I scripts/md2docx.py <manuscript.md> <out.docx> <mode>
#   mode "main"  : anonymized manuscript (masked title page, abstract, text, Declarations, Open Practices Statement,
#                  References); repository links and author contributions are removed for review
#   mode "title" : separate title page with author information and Author Note
#   mode "supp"  : Supplementary Material (reads supp/Supplementary_Material_en.md; landscape)
# Layout: US Letter, 1" margins, Times New Roman 12 pt, double spacing, page number top right (no running head);
# figures embedded after the paragraph that first cites them. Inline markup: **bold**, *italic*, x_sub / x_{sub},
# x^sup / x^(sup) / x^{sup}.
import re, sys
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt

TABLE_WIDTH = [6.5]
SRC, OUT = sys.argv[1], sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else 'main'
FIGS = {1: 'figs/fig1_keycell_recovery.png', 2: 'figs/fig2_recovery_by_cell.png',
        3: 'figs/fig3_shrinkage_careless.png', 4: 'figs/fig4_sbc.png'}
md = open(SRC, encoding='utf-8').read()

# ---------------------------------------------------------------- split the markdown into sections
def section(name, nxt):
    i = md.index(name); j = md.index(nxt, i + 1) if nxt else len(md); return md[i:j]
title = md.split('\n', 1)[0].lstrip('# ').strip()
abstract = section('## Abstract', '**Keywords').split('\n', 2)[2].strip()
keywords = re.search(r'\*\*Keywords:\*\*\s*(.+)', md).group(1).strip()
body = section('## Introduction', '## Open Practices Statement')
opens = section('## Open Practices Statement', '## Declarations')
decl = section('## Declarations', '## Figure captions')
caps = section('## Figure captions', '## References')
refs = section('## References', None)
ANON = '[link removed for anonymous review]'
if MODE == 'main':
    opens = re.sub(r'https://github\.com/\S+?(?=[;.,]?(\s|$))', ANON, opens)
    decl = re.sub(r'https://github\.com/\S+?(?=[;.,]?(\s|$))', ANON, decl)
    decl = re.sub(r"(\*\*Authors' contributions\.\*\*).*", r'\1 [Removed for anonymous review; provided on the title page.]', decl)
captions = {int(m.group(1)): (m.group(2).strip(), m.group(3).strip())
            for m in re.finditer(r'\*\*Figure (\d)\.\*\* \*(.+?)\*\s*(.+)', caps)}

# ---------------------------------------------------------------- document setup
doc = Document()
st = doc.styles['Normal']; st.font.name = 'Times New Roman'; st.font.size = Pt(12)
st.element.rPr.rFonts.set(qn('w:eastAsia'), 'Times New Roman')
pf = st.paragraph_format; pf.line_spacing_rule = WD_LINE_SPACING.DOUBLE; pf.space_before = Pt(0); pf.space_after = Pt(0)
sec = doc.sections[0]; sec.page_width, sec.page_height = Inches(8.5), Inches(11)
for s in ('left_margin', 'right_margin', 'top_margin', 'bottom_margin'): setattr(sec, s, Inches(1))

def field(run, code):
    for t, txt in (('begin', None), (None, code), ('end', None)):
        if t: e = OxmlElement('w:fldChar'); e.set(qn('w:fldCharType'), t)
        else: e = OxmlElement('w:instrText'); e.set(qn('xml:space'), 'preserve'); e.text = txt
        run._r.append(e)
hp = sec.header.paragraphs[0]; 
hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT; field(hp.add_run(), 'PAGE')   # page number only, no running head

# ---------------------------------------------------------------- inline parser
SUBRUN = r'[A-Za-z0-9Ͱ-Ͽ]+(?:,[A-Za-z0-9Ͱ-Ͽ]+)*'
def tokens(text, base=None):
    """Return list of (text, fmt) with fmt dict bold/italic/sub/sup."""
    fmt = dict(bold=False, italic=False, sub=False, sup=False); fmt.update(base or {})
    out, i, buf = [], 0, ''
    def flush():
        nonlocal buf
        if buf: out.append((buf, dict(fmt))); buf = ''
    while i < len(text):
        c = text[i]
        if c == '*':
            n = len(re.match(r'\*+', text[i:]).group(0)); flush()
            if n >= 3:
                if fmt['italic']: fmt['italic'] = False; fmt['bold'] = not fmt['bold']
                else: fmt['bold'] = not fmt['bold']; fmt['italic'] = True
                i += 3; continue
            if n == 2: fmt['bold'] = not fmt['bold']; i += 2; continue
            fmt['italic'] = not fmt['italic']; i += 1; continue
        if c in '_^' and i > 0 and not (c == '_' and text[i - 1].isalnum() and i + 1 < len(text) and text[i + 1].isdigit()) \
                and not (c == '_' and text[i - 1].isalnum() and text[i - 1].islower() and i >= 4 and text[i - 4:i].isalpha() and not text[max(0, i - 5):i].endswith('score')):
            key = 'sub' if c == '_' else 'sup'; rest = text[i + 1:]; inner = None; adv = 0
            if rest.startswith('{'):
                d = 0
                for k, ch in enumerate(rest):
                    d += ch == '{'; d -= ch == '}'
                    if d == 0: inner, adv = rest[1:k], k + 1; break
            elif rest.startswith('(') and key == 'sup':
                k = rest.index(')'); inner, adv = rest[1:k], k + 1
            elif rest.startswith('*'):
                m = re.match(r'\*[^*]+\*', rest); inner, adv = m.group(0), len(m.group(0))
            else:
                m = re.match(SUBRUN, rest)
                if m: inner, adv = m.group(0), len(m.group(0))
            if inner is not None:
                flush(); b = dict(fmt); b[key] = True; out.extend(tokens(inner, b)); i += 1 + adv; continue
        buf += c; i += 1
    flush(); return out

def add_inline(p, text, **extra):
    for t, f in tokens(text):
        r = p.add_run(t); r.bold = f['bold'] or extra.get('bold'); r.italic = f['italic'] or extra.get('italic')
        if f['sub']: r.font.subscript = True
        if f['sup']: r.font.superscript = True
    return p

def para(text='', indent=True, align=None, keep=False, **extra):
    p = doc.add_paragraph(); p.paragraph_format.first_line_indent = Inches(.5) if indent else Inches(0)
    if align: p.alignment = align
    if keep: p.paragraph_format.keep_with_next = True
    if text: add_inline(p, text, **extra)
    return p

def page_break(): doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

def heading(text, level):
    if level == 1: p = para(text, indent=False, align=WD_ALIGN_PARAGRAPH.CENTER, keep=True, bold=True)
    elif level == 2: p = para(text, indent=False, keep=True, bold=True)
    else: p = para(text, indent=False, keep=True, bold=True, italic=True)
    return p

def borders(cell, top=None, bottom=None):
    tcPr = cell._tc.get_or_add_tcPr(); b = OxmlElement('w:tcBorders')
    for side, val in (('top', top), ('bottom', bottom), ('left', None), ('right', None)):
        e = OxmlElement(f'w:{side}'); e.set(qn('w:val'), 'single' if val else 'nil')
        if val: e.set(qn('w:sz'), str(val)); e.set(qn('w:color'), '000000')
        b.append(e)
    tcPr.append(b)

def table(lines):
    rows = [[c.strip() for c in l.strip().strip('|').split('|')] for l in lines if not re.match(r'^\|[-|\s]+\|$', l.strip())]
    t = doc.add_table(rows=len(rows), cols=len(rows[0])); t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False; nc = len(rows[0]); w0 = 1.15 if TABLE_WIDTH[0] < 7 else 1.6; ws = [w0] + [(TABLE_WIDTH[0] - w0) / (nc - 1)] * (nc - 1)
    for j, w in enumerate(ws):
        for c in t.columns[j].cells: c.width = Inches(w)
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            c = t.cell(i, j); p = c.paragraphs[0]; p.paragraph_format.line_spacing = 1.0
            p.paragraph_format.keep_with_next = i < len(rows) - 1; p.paragraph_format.keep_together = True
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j == 0 else WD_ALIGN_PARAGRAPH.CENTER
            m = re.match(r'^(\S+) (\[.+\])$', val)
            if m:
                add_inline(p, m.group(1)); p.add_run().add_break(); add_inline(p, m.group(2))
            else: add_inline(p, val)
            for r in p.runs: r.font.size = Pt(10)
            borders(c, top=8 if i in (0, 1) else None, bottom=8 if i == len(rows) - 1 else None)

def figure(n):
    ttl, note = captions[n]
    para(f'Figure {n}', indent=False, keep=True, bold=True)
    para(ttl, indent=False, keep=True, italic=True)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(FIGS[n], width=Inches(6.5))
    p = para(indent=False); p.add_run('Note. ').italic = True; add_inline(p, note)

# ---------------------------------------------------------------- render blocks
placed = set()
def render(block_text, skip_first_heading=False):
    lines = block_text.split('\n'); i = 0; first = True
    while i < len(lines):
        l = lines[i]
        if not l.strip(): i += 1; continue
        if l.startswith('#'):
            lvl = len(l) - len(l.lstrip('#'))
            if not (skip_first_heading and first): heading(l.lstrip('# ').strip(), {2: 1, 3: 2}.get(lvl, 3))
            first = False; i += 1; continue
        first = False
        if l.startswith('|'):
            tl = []
            while i < len(lines) and lines[i].startswith('|'): tl.append(lines[i]); i += 1
            table(tl); continue
        m = re.match(r'^\*\*Table (S?\d+[a-c]?)\*\*$', l)
        if m:
            para(f'Table {m.group(1)}', indent=False, keep=True, bold=True)
            para(lines[i + 1].strip().strip('*'), indent=False, keep=True, italic=True); i += 2; continue
        if l.startswith('*Note.*'):
            p = para(indent=False); p.add_run('Note. ').italic = True; add_inline(p, l[len('*Note.*'):].strip()); i += 1; continue
        if re.match(r'^\d\. ', l):
            p = para(l, indent=False); p.paragraph_format.left_indent = Inches(.5); p.paragraph_format.first_line_indent = Inches(-.25); i += 1; continue
        if re.match(r'^(\*a\*_c\(θ\) =|\*\*[ab]\*\*\(\*t\* \+ 1\) =|\*\*M\*\*_\*r\*\^\*t\* =)', l):
            para(l.rstrip(',.'), indent=False, align=WD_ALIGN_PARAGRAPH.CENTER); i += 1; continue
        para(l, indent=not l.startswith('so that') and not l.startswith('where ') and not l.startswith('*a*_k(*t*) > 0') and not l.startswith('(**P**ᵀ)'))
        for n in sorted(set(int(x) for x in re.findall(r'Figures? (\d)(?:[ab])?', l) + re.findall(r'Figures \d and (\d)', l))):
            if n not in placed and n in FIGS: figure(n); placed.add(n)
        i += 1

if MODE == 'main':
    for _ in range(3): para(indent=False)
    para(title, indent=False, align=WD_ALIGN_PARAGRAPH.CENTER, bold=True)
    page_break()
    para('Abstract', indent=False, align=WD_ALIGN_PARAGRAPH.CENTER, bold=True)
    para(abstract, indent=False)
    p = para(); p.add_run('Keywords: ').italic = True; p.add_run(keywords)
    page_break()
    para(title, indent=False, align=WD_ALIGN_PARAGRAPH.CENTER, bold=True)
    render(body, skip_first_heading=True)
    render(decl); render(opens)
    page_break(); heading('References', 1)
    for l in refs.split('\n')[1:]:
        if l.strip():
            p = para(l.strip(), indent=False); p.paragraph_format.left_indent = Inches(.5); p.paragraph_format.first_line_indent = Inches(-.5)
    for n in sorted(set(FIGS) - placed): figure(n)
    print('figures placed after first citation:', sorted(placed))
elif MODE == 'title':
    # author details live in title_info.json (git-ignored): {"affiliation", "orcid", "address", "email"}
    import json, os
    TI = {'affiliation': '[Affiliation]', 'orcid': '[ORCID iD]', 'address': '[postal address]', 'email': '[email]'}
    if os.path.exists('title_info.json'): TI.update(json.load(open('title_info.json', encoding='utf-8')))
    for _ in range(3): para(indent=False)
    para(title, indent=False, align=WD_ALIGN_PARAGRAPH.CENTER, bold=True)
    para(indent=False)
    para('Bo Yuan', indent=False, align=WD_ALIGN_PARAGRAPH.CENTER)
    para(TI['affiliation'], indent=False, align=WD_ALIGN_PARAGRAPH.CENTER)
    for _ in range(3): para(indent=False)
    para('Author Note', indent=False, align=WD_ALIGN_PARAGRAPH.CENTER, bold=True)
    para('Bo Yuan ' + TI['orcid'])
    para('No funding was received for conducting this study. The author has no relevant financial or non-financial interests to disclose.')
    contrib = re.search(r"\*\*Authors' contributions\.\*\*\s*(.+)", decl).group(1).strip()
    para('CRediT author statement. ' + contrib)
    para(re.sub(r'^## Open Practices Statement\s*', '', opens).strip())
    para('Correspondence concerning this article should be addressed to Bo Yuan, ' + TI['address'] + '. Email: ' + TI['email'])
elif MODE == 'supp':
    sm = open('supp/Supplementary_Material_en.md', encoding='utf-8').read().split('\n')
    from docx.enum.section import WD_ORIENT
    sec.orientation = WD_ORIENT.LANDSCAPE; sec.page_width, sec.page_height = Inches(11), Inches(8.5)
    para('Supplementary Material', indent=False, align=WD_ALIGN_PARAGRAPH.CENTER, bold=True)
    para(sm[2].strip(), indent=False, align=WD_ALIGN_PARAGRAPH.CENTER, italic=True)
    TABLE_WIDTH[0] = 9.0
    render('\n'.join(sm[4:]))
doc.save(OUT); print('saved', OUT, '(' + MODE + ')')
