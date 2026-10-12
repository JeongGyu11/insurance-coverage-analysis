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
a=read('work/nh/revision/original.xlsx');b=read('outputs/01a10ed0-eb0e-7720-80fe-23aace7c950b/NH농협생명_2507_담보분석.xlsx')
r=json.loads(Path('work/nh/revision/revised.json').read_text(encoding='utf8'));old=json.loads(Path('work/nh/records.json').read_text(encoding='utf8'))
assert len(r)==83 and sum(x['product_name'].startswith('온라인') for x in r)==34
assert len([k for k in b[0] if re.fullmatch(r'A\d+',k)])==84
assert all(a[0][c+'1']==b[0][c+'1'] for c in 'ABCDEFGHI')
assert all(a[0][c+str(i)]==b[0][c+str(i)] for i in range(2,85) for c in 'ABCDH')
assert a[2]==b[2]
assert all(b[0][c+str(i)] for i in range(2,85) for c in 'EFGI')
for x,y in zip(old,r):
 for t in re.findall(r'[\d,]+(?:\.\d+)?(?:만원|천원|%|회|건)',x['coverage_amount']):assert t in y['coverage_amount'],(x['id'],t)
assert '일반 3형: 보장하지 않음' in r[3]['coverage_amount']
assert '3일 초과분' in r[5]['coverage_conditions'] and '120일' in r[5]['coverage_conditions']
assert all(s in r[10]['coverage_conditions'] for s in ['275일','365일','90일','180일','비례분담'])
assert '90회·90건' in r[11]['coverage_conditions']
assert '30%' in r[14]['coverage_amount'] and '350만원' in r[14]['coverage_amount']
assert 'SFTS(A93.80)' in r[34]['coverage_conditions'] and '휴일 발생 여부로' in r[41]['coverage_conditions']
assert '부목' in r[82]['coverage_conditions'] and '1회만' in r[82]['coverage_conditions']
assert not any('제3자' in x['coverage_conditions'] for x in r)
print('PASS: 83 rows, 49 offline/34 online, nine columns; identity/created_at/all sources preserved; original amounts/rates retained; medical deductibles, reinstatement, holiday exceptions and rider restrictions verified.')
