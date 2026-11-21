# Convert the manuscript markdown to APA 7 / Behavior Research Methods Word files.
# Usage (from 07_论文/): python3 -I scripts/md2docx.py <manuscript.md> <out.docx> <mode>
#   mode "full"  : manuscript for BRM (no blind review): title page, abstract, text, Declarations, Open Practices
#                  Statement, References; nothing masked
#   mode "main"  : anonymized manuscript (title and abstract on page 1, text, Declarations, Open Practices Statement,
#                  References); repository links and author contributions are removed for review
#   mode "title" : separate title page with author information and Author Note
#   mode "supp"  : Supplementary Material (reads supp/Supplementary_Material_en.md; landscape)
# Layout: US Letter, 1" margins, Times New Roman 12 pt, double spacing, page number upper right (no running head);
# display equations are native Word equations (OMML; see scripts/equations.py);
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
    # anonymous mirrors for reviewers (anonymous.4open.science, identifying terms redacted; expire 2027-04-20)
    MIRROR = {'https://github.com/gxnuyuanbo-hash/gvmodel-analysis': 'https://anonymous.4open.science/r/gvmodel-analysis-58CF/',
              'https://github.com/gxnuyuanbo-hash/gvmodel': 'https://anonymous.4open.science/r/gvmodel-5133/'}
    for k, v in MIRROR.items():
        opens = re.sub(re.escape(k) + r'(?![\w-])', v.rstrip('/'), opens); decl = re.sub(re.escape(k) + r'(?![\w-])', v.rstrip('/'), decl)
    opens = re.sub(r'https://github\.com/\S+?(?=[;.,]?(\s|$))', ANON, opens)
    opens = re.sub(r'archived on Zenodo \([^)]*\)', 'archived on Zenodo (DOIs withheld for anonymous review)', opens)   # Zenodo records show the author
    decl = re.sub(r' \(https://doi\.org/10\.5281/zenodo\.\d+\)', '', decl)   # DOI in parentheses after a masked link
    decl = re.sub(r'https://github\.com/\S+?(?=[;.,]?(\s|$))', ANON, decl)
    decl = re.sub(r"(\*\*Authors' contributions\.\*\*).*", r'\1 [Removed for anonymous review and provided on the title page.]', decl)
captions = {int(m.group(1)): (m.group(2).strip(), m.group(3).strip())
            for m in re.finditer(r'\*\*Figure (\d)\.\*\* \*(.+?)\*[ \t]*(.*)', caps)}

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
fp = sec.header.paragraphs[0]
fp.alignment = WD_ALIGN_PARAGRAPH.RIGHT; field(fp.add_run(), 'PAGE')   # BRM: page number upper right, no running head

# ---------------------------------------------------------------- display equations (MathML -> OMML)
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from equations import EQS, XSL, mathml
from lxml import etree
TO_OMML = etree.XSLT(etree.parse(XSL)) if XSL else None
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
def mel(tag, **attrs):
    e = etree.SubElement(etree.Element('dummy'), '{%s}%s' % (M, tag))
    for k, v in attrs.items(): e.set('{%s}%s' % (M, k), v)
    return e
def mrun(text):
    r = mel('r'); t = etree.SubElement(r, '{%s}t' % M); t.text = text; return r
def equation(body, label):
    # display equation; a numbered one sits in a borderless 3-column table (blank | equation | number) so the
    # number stays flush right in Word and in ScholarOne's PDF converter, which ignores Word's "#" numbering
    omath = TO_OMML(etree.fromstring(mathml(body))).getroot()
    if etree.QName(omath).localname == 'oMathPara': omath = omath.find('{%s}oMath' % M)   # the XSL wraps block math
    for pr in omath.iter('{%s}naryPr' % M):            # limits above and below the sum (limLoc follows chr)
        if pr.find('{%s}limLoc' % M) is None:
            pos = 1 if len(pr) and pr[0].tag == '{%s}chr' % M else 0; pr.insert(pos, mel('limLoc', val='undOvr'))
    mp = mel('oMathPara'); mp.append(omath)
    if not label:
        p = doc.add_paragraph(); p.paragraph_format.first_line_indent = Inches(0); p._p.append(mp); return p
    W = TABLE_WIDTH[0]; ws = [0.7, W - 1.4, 0.7]
    t = doc.add_table(rows=1, cols=3); t.alignment = WD_TABLE_ALIGNMENT.CENTER; t.autofit = False
    for j, w in enumerate(ws):
        c = t.cell(0, j); c.width = Inches(w); borders(c)
        c.vertical_alignment = 1                            # center
        q = c.paragraphs[0]; q.paragraph_format.first_line_indent = Inches(0)
    t.cell(0, 1).paragraphs[0]._p.append(mp)
    q = t.cell(0, 2).paragraphs[0]; q.alignment = WD_ALIGN_PARAGRAPH.RIGHT; q.add_run('(' + label + ')')
    return t
# math font that matches Times New Roman (falls back to Cambria Math where STIX Two Math is not installed)
_set = doc.settings.element
mpr = _set.find('{%s}mathPr' % M)                       # the default template already has one: set its font
if mpr is not None:
    mf = mpr.find('{%s}mathFont' % M)
    if mf is None: mf = mel('mathFont'); mpr.insert(0, mf)
    mf.set('{%s}val' % M, 'STIX Two Math')
z = _set.find(qn('w:zoom'))
if z is not None and z.get(qn('w:percent')) is None: z.set(qn('w:percent'), '100')
AFTER_MATHPR = ['attachedSchema', 'themeFontLang', 'clrSchemeMapping', 'doNotIncludeSubdocsInStats', 'doNotAutoCompressPictures',
                'forceUpgrade', 'captions', 'readModeInkLockDown', 'smartTagType', 'schemaLibrary', 'shapeDefaults',
                'doNotEmbedSmartTags', 'decimalSymbol', 'listSeparator']
if mpr is None:
    mpr = mel('mathPr'); mpr.append(mel('mathFont', val='STIX Two Math'))
    _nxt = next((c for c in _set if etree.QName(c).localname in AFTER_MATHPR), None)
    if _nxt is not None: _nxt.addprevious(mpr)
    else: _set.append(mpr)

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

URL_RE = re.compile(r'https?://[^\s)\]]+?(?=[.,;:]?(?:\s|$|\)|\]))|[\w.+-]+@[\w-]+(?:\.[\w-]+)+(?<!\.)')   # web addresses, DOIs, e-mail
LINK_BLUE = '0070C0'                                            # Word standard colour "Blue"
def link_style():
    # one character style "Hyperlink" in Word's standard colour Blue (0070C0), underlined: change it once in
    # Format > Style and every link in the document follows
    from docx.enum.style import WD_STYLE_TYPE
    from docx.shared import RGBColor
    names = [st.name for st in doc.styles]
    if 'Hyperlink' in names: hs = doc.styles['Hyperlink']
    else: hs = doc.styles.add_style('Hyperlink', WD_STYLE_TYPE.CHARACTER)
    hs.font.color.rgb = RGBColor.from_string(LINK_BLUE); hs.font.underline = True
    return hs.style_id

def add_link(p, url, size=None, target=None):
    from docx.opc.constants import RELATIONSHIP_TYPE as RT
    rid = p.part.relate_to(target or url, RT.HYPERLINK, is_external=True)
    h = OxmlElement('w:hyperlink'); h.set(qn('r:id'), rid)
    r = OxmlElement('w:r'); rpr = OxmlElement('w:rPr')
    if LINK_STYLE[0] is None: LINK_STYLE[0] = link_style()
    rs = OxmlElement('w:rStyle'); rs.set(qn('w:val'), LINK_STYLE[0]); rpr.append(rs)
    if size:
        sz = OxmlElement('w:sz'); sz.set(qn('w:val'), str(int(size * 2))); rpr.append(sz)
    r.append(rpr); t = OxmlElement('w:t'); t.text = url; t.set(qn('xml:space'), 'preserve'); r.append(t)
    h.append(r); p._p.append(h)
LINK_STYLE = [None]

def add_inline(p, text, **extra):
    text = re.sub(r' ([=<>≤≥∈~]) (?=[\d.−\-+(*_A-Za-zα-ωΑ-Ω](?:[^A-Za-z]|$))', '\u00a0\\1\u00a0', text)   # keep relations with short operands together
    pos = 0
    for m in URL_RE.finditer(text):                          # web addresses and DOIs become live links
        u = m.group(0); _add_runs(p, text[pos:m.start()], **extra)
        add_link(p, u, target=None if u.startswith('http') else 'mailto:' + u); pos = m.end()
    _add_runs(p, text[pos:], **extra)
    return p

def rhat(p, letter='R', italic=True):
    # hatted letter (R-hat, d-hat, r-hat) as a native Word accent: the combining circumflex (U+0302) drifts off
    # the letter in ScholarOne's PDF converter
    om = etree.Element('{%s}oMath' % M); acc = etree.SubElement(om, '{%s}acc' % M)
    pr = etree.SubElement(acc, '{%s}accPr' % M); c = etree.SubElement(pr, '{%s}chr' % M); c.set('{%s}val' % M, '\u0302')
    e = etree.SubElement(acc, '{%s}e' % M); e.append(mrun(letter)); p._p.append(om)

def _add_runs(p, text, **extra):
    m = re.search(r'([A-Za-z])\u0302', text)
    if m:
        _add_runs(p, text[:m.start()], **extra); rhat(p, m.group(1)); _add_runs(p, text[m.end():], **extra)
        return
    for t, f in tokens(text):
        r = p.add_run(t); r.bold = f['bold'] or extra.get('bold'); r.italic = f['italic'] or extra.get('italic')
        if f['sub']: r.font.subscript = True
        if f['sup']: r.font.superscript = True

def para(text='', indent=True, align=None, keep=False, **extra):
    p = doc.add_paragraph(); p.paragraph_format.first_line_indent = Inches(.5) if indent else Inches(0)
    p.alignment = align if align is not None else WD_ALIGN_PARAGRAPH.JUSTIFY   # body text justified
    if keep: p.paragraph_format.keep_with_next = True
    if text: add_inline(p, text, **extra)
    return p

def page_break(): doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

SUPP_LEFT = [False]
def heading(text, level):
    if level == 1 and SUPP_LEFT[0]:
        p = para(text, indent=False, align=WD_ALIGN_PARAGRAPH.LEFT, keep=True, bold=True)
        p.paragraph_format.space_before = Pt(18); p.paragraph_format.space_after = Pt(4)
    elif level == 1: p = para(text, indent=False, align=WD_ALIGN_PARAGRAPH.CENTER, keep=True, bold=True)
    elif level == 2: p = para(text, indent=False, align=WD_ALIGN_PARAGRAPH.LEFT, keep=True, bold=True)
    else: p = para(text, indent=False, align=WD_ALIGN_PARAGRAPH.LEFT, keep=True, bold=True, italic=True)
    return p

def borders(cell, top=None, bottom=None):
    tcPr = cell._tc.get_or_add_tcPr(); b = OxmlElement('w:tcBorders')
    for side, val in (('top', top), ('left', None), ('bottom', bottom), ('right', None)):   # schema order
        e = OxmlElement(f'w:{side}'); e.set(qn('w:val'), 'single' if val else 'nil')
        if val: e.set(qn('w:sz'), str(val)); e.set(qn('w:color'), '000000')
        b.append(e)
    tcPr.append(b)

def table(lines):
    rows = [[c.strip() for c in l.strip().strip('|').split('|')] for l in lines if not re.match(r'^\|[-|\s]+\|$', l.strip())]
    t = doc.add_table(rows=len(rows), cols=len(rows[0])); t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False; nc = len(rows[0])
    longest = max(len(re.sub(r'[*_]', '', r[0])) for r in rows)          # first column as wide as its content needs
    w0 = min(1.15 if TABLE_WIDTH[0] < 7 else 1.6, max(.5, .06 * longest + .12)); ws = [w0] + [(TABLE_WIDTH[0] - w0) / (nc - 1)] * (nc - 1)
    for j, w in enumerate(ws):
        for c in t.columns[j].cells: c.width = Inches(w)
    has_ci = any(re.search(r'\[.+,.+\]', v) for r in rows for v in r)
    size = 10 if nc < 8 or not has_ci else 9                              # intervals need room in wide tables
    if nc >= 12: size = 7                                                  # very wide supplementary tables
    tblPr = t._tbl.tblPr; mar = OxmlElement('w:tblCellMar')               # narrow cell margins (0.03 in)
    for side in ('left', 'right'):
        e = OxmlElement(f'w:{side}'); e.set(qn('w:w'), '43'); e.set(qn('w:type'), 'dxa'); mar.append(e)
    look = tblPr.find(qn('w:tblLook'))                                   # schema order: tblCellMar before tblLook
    if look is not None: look.addprevious(mar)
    else: tblPr.append(mar)
    for i, row in enumerate(rows):
        trPr = t.rows[i]._tr.get_or_add_trPr(); cs = OxmlElement('w:cantSplit'); trPr.append(cs)   # rows never split
        for j, val in enumerate(row):
            c = t.cell(i, j); p = c.paragraphs[0]; p.paragraph_format.line_spacing = 1.0
            p.paragraph_format.keep_with_next = i < len(rows) - 1; p.paragraph_format.keep_together = True
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j == 0 else WD_ALIGN_PARAGRAPH.CENTER
            m = re.match(r'^(\S+) (\[.+\])$', val)
            if m:                                                         # estimate, line break, [lower,\u00a0upper]
                add_inline(p, m.group(1)); p.add_run().add_break(); add_inline(p, m.group(2).replace(', ', ',\u00a0'))
            else: add_inline(p, val)
            for r in p.runs:
                r.font.size = Pt(size)
                if i == 0 and SUPP_LEFT[0]: r.bold = True
            for mr in p._p.iter('{%s}r' % M):                          # hatted letters (OMML) at the table's size
                rpr = OxmlElement('w:rPr')
                if i == 0 and SUPP_LEFT[0]: rpr.append(OxmlElement('w:b'))
                sz = OxmlElement('w:sz'); sz.set(qn('w:val'), str(int(size * 2))); rpr.append(sz); mr.insert(0, rpr)
            borders(c, top=8 if i in (0, 1) else None, bottom=8 if i == len(rows) - 1 else None)

def figure(n):
    ttl, note = captions[n]
    para(f'Figure {n}', indent=False, align=WD_ALIGN_PARAGRAPH.LEFT, keep=True, bold=True)
    para(ttl, indent=False, align=WD_ALIGN_PARAGRAPH.LEFT, keep=True, italic=True)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(FIGS[n], width=Inches(6.5))
    if note: p = para(indent=False); p.add_run('Note. ').italic = True; add_inline(p, note)   # details are in the text

# ---------------------------------------------------------------- render blocks
placed = set()
NUM = [False, 0, 0]                                       # numbered headings in the body: 1, 1.1, ...
def numbered(text, lvl):
    if not NUM[0]: return text
    if lvl == 2: NUM[1] += 1; NUM[2] = 0; return f'{NUM[1]} {text}'
    if lvl == 3: NUM[2] += 1; return f'{NUM[1]}.{NUM[2]} {text}'
    return text
def render(block_text, skip_first_heading=False):
    lines = block_text.split('\n'); i = 0; first = True
    while i < len(lines):
        l = lines[i]
        if not l.strip(): i += 1; continue
        if l.startswith('#'):
            lvl = len(l) - len(l.lstrip('#'))
            if not (skip_first_heading and first): heading(numbered(l.lstrip('# ').strip(), lvl), {2: 1, 3: 2}.get(lvl, 3))
            first = False; i += 1; continue
        first = False
        if l.startswith('|'):
            tl = []
            while i < len(lines) and lines[i].startswith('|'): tl.append(lines[i]); i += 1
            table(tl); continue
        m = re.match(r'^\*\*(Table S\d+\.) (.+)\*\*$', l)          # supplement: "Table S1. Title" on one line
        if m:
            p = para(indent=False, align=WD_ALIGN_PARAGRAPH.LEFT, keep=True); p.paragraph_format.space_before = Pt(18)
            p.paragraph_format.space_after = Pt(4); add_inline(p, m.group(1) + ' ' + m.group(2), bold=True); i += 1; continue
        m = re.match(r'^\*\*Table (S?\d+[a-c]?)\*\*$', l)
        if m:
            para(f'Table {m.group(1)}', indent=False, align=WD_ALIGN_PARAGRAPH.LEFT, keep=True, bold=True)
            para(lines[i + 1].strip().strip('*'), indent=False, align=WD_ALIGN_PARAGRAPH.LEFT, keep=True, italic=True); i += 2; continue
        if l.startswith('*Note.*'):
            p = para(indent=False); p.add_run('Note. ').italic = True; add_inline(p, l[len('*Note.*'):].strip()); i += 1; continue
        if re.match(r'^\d\. ', l):
            p = para(l, indent=False); p.paragraph_format.left_indent = Inches(.5); p.paragraph_format.first_line_indent = Inches(-.25); i += 1; continue
        eq = next((k for k in EQS if re.match(k, l)), None)
        if eq:
            if TO_OMML is None: raise SystemExit('mathml2omml.xsl not found: install Microsoft Word or set XSL in equations.py')
            equation(*EQS[eq]); i += 1; continue
        para(l, indent=not SUPP_LEFT[0] and not l.startswith('so that') and not l.startswith('where ') and not l.startswith('*a*_k(*t*) > 0') and not l.startswith('(**P**ᵀ)') and not l.startswith('Here *vᵢ*'))
        for n in sorted(set(int(x) for x in re.findall(r'Figures? (\d)(?:[ab])?', l) + re.findall(r'Figures \d and (\d)', l))):
            if n not in placed and n in FIGS: figure(n); placed.add(n)
        i += 1

def title_page(full_note=True):
    # author details live in title_info.json (git-ignored): {"affiliation", "orcid", "address", "phone", "email"}
    import json, os
    TI = {'affiliation': '[Affiliation]', 'orcid': '[ORCID iD]', 'address': '[postal address]', 'phone': '[telephone]', 'email': '[email]'}
    if os.path.exists('title_info.json'): TI.update(json.load(open('title_info.json', encoding='utf-8')))
    L = WD_ALIGN_PARAGRAPH.LEFT; C = WD_ALIGN_PARAGRAPH.CENTER
    p = para(title, indent=False, align=C, bold=True)          # user's layout: title at the top, 16 pt
    for r in p.runs: r.font.size = Pt(16)
    para(indent=False)
    para('Bo Yuan', indent=False, align=C)
    para(TI['address'], indent=False, align=C)
    for _ in range(2): para(indent=False)
    p = para(indent=False, align=L); p.add_run('Corresponding author: ').bold = True; add_inline(p, 'Bo Yuan, ' + TI['address'])   # BRM: address, telephone, e-mail
    p = para(indent=False, align=L); p.add_run('Telephone: ').bold = True; add_inline(p, TI['phone'])
    p = para(indent=False, align=L); p.add_run('Email: ').bold = True; add_inline(p, TI['email'])
    p = para(indent=False, align=L); p.add_run('ORCID: ').bold = True; add_inline(p, 'Bo Yuan, ' + TI['orcid'])
    if full_note:                                           # separate title page: also funding, CRediT and open practices
        p = para(indent=False, align=L); p.add_run('Funding and competing interests: ').bold = True
        add_inline(p, 'No funding was received for conducting this study. The author has no relevant financial or non-financial interests to disclose.')
        contrib = re.search(r"\*\*Authors' contributions\.\*\*\s*(.+)", decl).group(1).strip()
        p = para(indent=False, align=L); p.add_run('CRediT author statement: ').bold = True; add_inline(p, contrib)

if MODE == 'full':
    # BRM does not use blind review: one manuscript file with the title page first, nothing masked
    title_page(full_note=False); page_break()
    para('Abstract', indent=False, align=WD_ALIGN_PARAGRAPH.CENTER, bold=True)
    para(abstract, indent=False)
    p = para(); p.add_run('Keywords: ').italic = True; p.add_run(keywords)
    page_break()
    para(title, indent=False, align=WD_ALIGN_PARAGRAPH.CENTER, bold=True)
    render(body)
    render(decl); render(opens)
    page_break(); heading('References', 1)
    for l in refs.split('\n')[1:]:
        if l.strip():
            p = para(l.strip(), indent=False, align=WD_ALIGN_PARAGRAPH.LEFT); p.paragraph_format.left_indent = Inches(.5); p.paragraph_format.first_line_indent = Inches(-.5)
    for n in sorted(set(FIGS) - placed): figure(n)
    print('figures placed after first citation:', sorted(placed))
elif MODE == 'main':
    para(title, indent=False, align=WD_ALIGN_PARAGRAPH.CENTER, bold=True)   # title and abstract on page 1
    para(indent=False)
    para('Abstract', indent=False, align=WD_ALIGN_PARAGRAPH.CENTER, bold=True)
    para(abstract, indent=False)
    p = para(); p.add_run('Keywords: ').italic = True; p.add_run(keywords)
    page_break()
    para(title, indent=False, align=WD_ALIGN_PARAGRAPH.CENTER, bold=True)
    render(body)   # APA: unnumbered headings; keeps the "Introduction" heading, as in published BRM articles
    render(decl); render(opens)
    page_break(); heading('References', 1)
    for l in refs.split('\n')[1:]:
        if l.strip():
            p = para(l.strip(), indent=False, align=WD_ALIGN_PARAGRAPH.LEFT); p.paragraph_format.left_indent = Inches(.5); p.paragraph_format.first_line_indent = Inches(-.5)
    for n in sorted(set(FIGS) - placed): figure(n)
    print('figures placed after first citation:', sorted(placed))
elif MODE == 'title':
    title_page(full_note=True)
elif MODE == 'supp':
    # layout follows a plain supplementary file: portrait, single spacing (1.15, 10 pt after), no page numbers,
    # centered title, then "Section S1." and "Table S1." blocks with bold left-aligned titles
    sm = open('supp/Supplementary_Material_en.md', encoding='utf-8').read().split('\n')
    fp._p.getparent().remove(fp._p); sec.header.add_paragraph()           # no page number
    pf.line_spacing = 1.15; pf.space_after = Pt(10)
    SUPP_LEFT[0] = True
    p = para('Supplementary Material', indent=False, align=WD_ALIGN_PARAGRAPH.CENTER, bold=True)
    for r in p.runs: r.font.size = Pt(16)
    p = para(sm[2].strip(), indent=False, align=WD_ALIGN_PARAGRAPH.CENTER, bold=True)
    for r in p.runs: r.font.size = Pt(16)
    para(indent=False, align=WD_ALIGN_PARAGRAPH.CENTER)
    render('\n'.join(sm[4:]))
doc.core_properties.author = doc.core_properties.last_modified_by = 'Bo Yuan'   # file metadata
doc.save(OUT); print('saved', OUT, '(' + MODE + ')')
