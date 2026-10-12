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
a=read('work/nh_nonlife/revision/original.xlsx');b=read('outputs/01a10ed0-eb0e-7720-80fe-23aace7c950b/NH농협손해보험_2507_담보분석.xlsx')
r=json.loads(Path('work/nh_nonlife/revision/revised.json').read_text(encoding='utf8'));old=json.loads(Path('work/nh_nonlife/records.json').read_text(encoding='utf8'))
assert len(r)==748 and len({x['product_name'] for x in r})==10
assert len([k for k in b[0] if re.fullmatch(r'A\d+',k)])==749
assert all(a[0][c+'1']==b[0][c+'1'] for c in 'ABCDEFGHI')
assert all(a[0][c+str(i)]==b[0][c+str(i)] for i in range(2,750) for c in 'ABCDH')
assert a[2]==b[2]
assert all(b[0][c+str(i)] for i in range(2,750) for c in 'EFGI')
for x,y in zip(old,r):
 for token in re.findall(r'[\d,]+(?:\.\d+)?\s*(?:만원|천원|억원|%|회)',x['coverage_amount']):
  t=re.sub(r'\s+','',token);new=re.sub(r'\s+','',' '.join(y[k] for k in ['coverage_amount','coverage_conditions','coverage_target']))
  assert t in new,(x['id'],t)
assert '90일' in r[7]['coverage_conditions'] and '50%' in r[7]['coverage_amount']
assert '자기부담금' in r[69]['coverage_amount'] and '합산' in r[69]['coverage_conditions']
assert '보험료' in r[106]['coverage_amount'] and '면제' in r[106]['coverage_amount']
assert '산모' in r[399]['coverage_target']
assert '50만원' in r[747]['coverage_conditions'] and '20만원' in r[747]['coverage_conditions']
assert not any('제3자' in x['coverage_conditions'] for x in r)
print('PASS: 748 rows/10 product types/nine columns; identities, created_at and all sources preserved; original monetary values/rates/counts retained; cancer waiting/reduction, pet deductibles, waiver and liability checks passed.')
