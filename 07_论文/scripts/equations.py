# Display equations as MathML, converted to native Word equations (OMML) by md2docx.py with the
# mathml2omml.xsl stylesheet that ships with Microsoft Word. Each key is a regex matched against the start of
# the markdown line that holds the equation; the markdown keeps a plain-text version for reading.
# Conventions (APA 7): variables italic, vectors and matrices bold upright, Greek letters and operators upright.
import os

XSL_CANDIDATES = ['/Applications/Microsoft Word.app/Contents/Resources/mathml2omml.xsl',
                  r'C:\Program Files\Microsoft Office\root\Office16\MML2OMML.XSL']
XSL = next((p for p in XSL_CANDIDATES if os.path.exists(p)), None)

def i(x): return f'<mi>{x}</mi>'                                  # italic variable
def g(x): return f'<mi mathvariant="normal">{x}</mi>'             # upright Greek / function name
def B(x): return f'<mi mathvariant="bold">{x}</mi>'               # bold vector / matrix
def o(x): return f'<mo>{x}</mo>'
def n(x): return f'<mn>{x}</mn>'
def r(*xs): return '<mrow>' + ''.join(xs) + '</mrow>'
def sub(a, b): return f'<msub>{a}{b}</msub>'
def sup(a, b): return f'<msup>{a}{b}</msup>'
def subsup(a, b, c): return f'<msubsup>{a}{b}{c}</msubsup>'
def paren(*xs): return r(o('('), r(*xs), o(')'))   # inner mrow: keeps operators as operators, not separators
def brack(*xs): return r(o('['), r(*xs), o(']'))
def frac(a, b): return f'<mfrac>{a}{b}</mfrac>'
def gap(): return '<mtext>\u2003</mtext>'                       # em space (mspace is dropped by the XSL)
def text(x): return f'<mtext>{x}</mtext>'
def sumover(lo, hi): return f'<munderover><mo>∑</mo>{lo}{hi}</munderover>'

PT = sup(B('P'), g('T'))
ONE_MINUS = lambda x: paren(n('1'), o('−'), x)

EQS = {
    # Manuscript, "Activation"
    r'^\*a\*_c\(θ\) =': r(
        sub(i('a'), i('c')), paren(g('θ')), o('='), ONE_MINUS(g('θ')),
        sumover(r(i('t'), o('='), n('0')), o('∞')), sup(g('θ'), i('t')), sup(paren(PT), i('t')), sub(B('e'), i('c')), o(',')),
    # Supplementary Material S1, setting
    r'^\*\*a\*\*\(\*t\* \+ 1\) =': r(
        B('a'), paren(i('t'), o('+'), n('1')), o('='), sub(i('T'), g('ε')),
        brack(ONE_MINUS(i('d')), sub(B('M'), i('r')), B('a'), paren(i('t'))), o(','),
        text('\u2003with\u2003'),
        sub(B('M'), i('r')), o('='), i('r'), B('I'), o('+'), ONE_MINUS(i('r')), PT, o(',')),
    # Supplementary Material S1, Property 2
    r'^\*\*b\*\*\(\*t\* \+ 1\) =': r(
        B('b'), paren(i('t'), o('+'), n('1')), o('='), sub(i('T'), sub(g('ε'), i('t'))),
        paren(sub(B('M'), i('r')), B('b'), paren(i('t'))), o(','), gap(),
        sub(g('ε'), i('t')), o('='),
        frac(r(g('ε'), o('/'), i('A')), sup(ONE_MINUS(i('d')), r(i('t'), o('+'), n('1')))), o(','), gap(),
        B('b'), paren(n('0')), o('='), sub(B('e'), i('C')), o('.')),
    # Supplementary Material S1, Property 3
    r'^\*\*M\*\*_\*r\*\^\*t\* =': r(
        subsup(B('M'), i('r'), i('t')), o('='), sumover(r(i('k'), o('='), n('0')), i('t')),
        r(o('('), '<mfrac linethickness="0">' + i('t') + i('k') + '</mfrac>', o(')')),
        sup(ONE_MINUS(i('r')), i('k')), sup(i('r'), r(i('t'), o('−'), i('k'))), sup(paren(PT), i('k')), o('.')),
}

def mathml(body):
    return f'<math xmlns="http://www.w3.org/1998/Math/MathML" display="block">{body}</math>'
