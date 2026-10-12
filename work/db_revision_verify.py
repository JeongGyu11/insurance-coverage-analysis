import json,re,zipfile
from pathlib import Path
from lxml import etree as E
N={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def read(p):
 with zipfile.ZipFile(p) as z:
  ss=[]
  if 'xl/sharedStrings.xml' in z.namelist():ss=[''.join(x.itertext()) for x in E.fromstring(z.read('xl/sharedStrings.xml'))]
  out=[]
  for i in range(1,4):
   cells={};root=E.fromstring(z.read(f'xl/worksheets/sheet{i}.xml'))
   for c in root.findall('.//s:sheetData/s:row/s:c',N):
    v=c.find('s:v',N);v=v.text if v is not None else ''
    if c.get('t')=='s':v=ss[int(v)]
    elif c.get('t')=='inlineStr':v=''.join(c.find('s:is',N).itertext())
    cells[c.get('r')]=v
   out.append(cells)
  return out
a=read('work/db/revision/original.xlsx');b=read('outputs/01a10ed0-eb0e-7720-80fe-23aace7c950b/DB생명_2507_담보분석.xlsx')
r=json.loads(Path('work/db/revision/revised.json').read_text(encoding='utf8'));old=json.loads(Path('work/db/records.json').read_text(encoding='utf8'))
assert len(r)==19 and len([k for k in b[0] if re.fullmatch(r'A\d+',k)])==20
assert all(a[0][c+'1']==b[0][c+'1'] for c in 'ABCDEFGHI')
assert all(a[0][c+str(i)]==b[0][c+str(i)] for i in range(2,21) for c in 'ABCDH')
assert all(a[2][c+str(i)]==b[2][c+str(i)] for i in range(2,21) for c in 'ABCDEFGI')
assert all(b[0][c+str(i)] for i in range(2,21) for c in 'EFGI')
for x,y in zip(old,r):
 for t in re.findall(r'[\d,]+(?:\.\d+)?(?:만원|억|%)',x['coverage_amount']):assert t in y['coverage_amount'],(x['id'],t)
assert '10배' in r[0]['coverage_amount'] and '2배' in r[15]['coverage_amount']
assert '1년 미만' in r[12]['coverage_amount'] and '10만원' in r[12]['coverage_amount']
assert all('추가하여 지급' in r[i-1]['coverage_conditions'] for i in [5,6,18,19])
assert '연간 1회' in r[13]['coverage_conditions'] and '변연절제술' not in r[13]['coverage_conditions']
assert '5년 이상' in r[15]['coverage_conditions'] and '20%' in r[15]['coverage_conditions']
print('PASS: 19 rows, nine columns; identities/created_at/source metadata preserved; all original money/rate tokens retained; benefit formulas, reductions, additional payments and surgery exceptions verified.')
