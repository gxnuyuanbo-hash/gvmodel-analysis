# Convert cover_letter_draft.md to cover_letter.docx (letter layout: single spacing, 12 pt after paragraphs).
# Usage (from 07_论文/): python3 -I scripts/cover_letter_docx.py
import re
from docx import Document
from docx.shared import Pt, Inches
from docx.oxml.ns import qn
paras = open('cover_letter_draft.md', encoding='utf-8').read().strip().split('\n\n')
doc = Document()
st = doc.styles['Normal']; st.font.name = 'Times New Roman'; st.font.size = Pt(12)
st.element.rPr.rFonts.set(qn('w:eastAsia'), 'Times New Roman')
st.paragraph_format.space_before = Pt(0); st.paragraph_format.space_after = Pt(12); st.paragraph_format.line_spacing = 1.0
sec = doc.sections[0]; sec.page_width, sec.page_height = Inches(8.5), Inches(11)
for s in ('left_margin', 'right_margin', 'top_margin', 'bottom_margin'): setattr(sec, s, Inches(1))
for block in paras:
    p = doc.add_paragraph()
    lines = block.split('\n')
    for k, line in enumerate(lines):
        for m in re.split(r'(\*[^*]+\*)', line):           # *italic*
            if not m: continue
            r = p.add_run(m.strip('*') if m.startswith('*') else m); r.italic = m.startswith('*')
        if k < len(lines) - 1: p.add_run().add_break()
    if block.startswith('Dear') or block.startswith('Sincerely'): p.paragraph_format.space_after = Pt(12)
    else: p.paragraph_format.alignment = 3 if len(block) > 200 else None   # justify body paragraphs
z = doc.settings.element.find(qn('w:zoom'))
if z is not None and z.get(qn('w:percent')) is None: z.set(qn('w:percent'), '100')   # schema-required attribute
doc.save('cover_letter.docx'); print('saved cover_letter.docx')
