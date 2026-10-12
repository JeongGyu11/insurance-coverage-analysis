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
a=read('work/kb/revision/original.xlsx');b=read('outputs/01a10ed0-eb0e-7720-80fe-23aace7c950b/KB라이프생명_2507_담보분석.xlsx')
r=json.loads(Path('work/kb/revision/revised.json').read_text(encoding='utf8'));old=json.loads(Path('work/kb/records.json').read_text(encoding='utf8'))
assert len(r)==24 and len({x['product_name'] for x in r})==6
assert len([k for k in b[0] if re.fullmatch(r'A\d+',k)])==25
assert all(a[0][c+'1']==b[0][c+'1'] for c in 'ABCDEFGHI')
assert all(a[0][c+str(i)]==b[0][c+str(i)] for i in range(2,26) for c in 'ABCDH')
assert a[2]==b[2]
assert all(b[0][c+str(i)] for i in range(2,26) for c in 'EFGI')
for x,y in zip(old,r):
 for t in re.findall(r'[\d,]+(?:\.\d+)?(?:만원|억원|억5천만원|회|%)',x['coverage_amount']):assert t in y['coverage_amount']+' '+y['coverage_conditions']+' '+y['coverage_target'],(x['id'],t)
assert '20배' in r[0]['coverage_amount'] and '1억5천만원' in r[1]['coverage_amount']
assert '중복 지급' in r[2]['coverage_conditions'] and '84회' in r[5]['coverage_amount']
assert '36회' in r[14]['coverage_amount'] and '1,440만원' in r[14]['coverage_amount']
assert '미보증형 산출 기준' in r[15]['coverage_amount'] and '最저' not in r[15]['coverage_amount']
assert '130%' in r[20]['coverage_amount'] and '2%' in r[20]['coverage_amount']
assert '납입면제' not in ''.join(x['coverage_conditions'] for x in r)
print('PASS: 24 rows, 6 product types, nine columns; identities/created_at/all source cells preserved; original payment values and rates retained; dementia/annuity conditions verified.')
