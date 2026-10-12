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
a=read('work/kyobo/revision/original.xlsx');b=read('outputs/01a10ed0-eb0e-7720-80fe-23aace7c950b/교보생명_2507_담보분석.xlsx')
r=json.loads(Path('work/kyobo/revision/revised.json').read_text(encoding='utf8'));old=json.loads(Path('work/kyobo/records.json').read_text(encoding='utf8'))
assert len(r)==283 and len({x['product_name'] for x in r})==6
assert len([k for k in b[0] if re.fullmatch(r'A\d+',k)])==284
assert all(a[0][c+'1']==b[0][c+'1'] for c in 'ABCDEFGHI')
assert all(a[0][c+str(i)]==b[0][c+str(i)] for i in range(2,285) for c in 'ABCDH')
assert a[2]==b[2]
assert all(b[0][c+str(i)] for i in range(2,285) for c in 'EFGI')
for x,y in zip(old,r):
 for token in re.findall(r'[\d,]+(?:\.\d+)?\s*(?:만원|천원|억원|%|회)',x['coverage_amount']):
  t=re.sub(r'\s+','',token);new=re.sub(r'\s+','',' '.join(y[k] for k in ['coverage_amount','coverage_conditions','coverage_target']))
  assert t in new,(x['id'],t)

