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
a=read('work/aig/revision/original.xlsx');b=read('outputs/01a10ed0-eb0e-7720-80fe-23aace7c950b/AIG손해보험_2507_담보분석.xlsx')
r=json.loads(Path('work/aig/revision/revised.json').read_text(encoding='utf8'));old=json.loads(Path('work/aig/records.json').read_text(encoding='utf8'))
assert a[2]==b[2]
assert len(r)==122
assert len([k for k in b[0] if re.fullmatch(r'A\d+',k)])==123
assert all(a[0][c+str(i)]==b[0][c+str(i)] for i in range(2,124) for c in 'ABCDH')
assert all(a[0][c+'1']==b[0][c+'1'] for c in 'ABCDEFGHI')
assert all(b[0][c+str(i)] for i in range(2,124) for c in 'EFGI')
assert all(set(re.findall(r'\d+(?:\.\d+)?%',x['amount'])).issubset(set(re.findall(r'\d+(?:\.\d+)?%',y['amount']))) for x,y in zip(old,r))
assert '2년' in r[3]['conditions']
assert '365일' in r[34]['conditions']
assert '100%' in r[26]['amount'] and '입원 1일당' in r[26]['amount']
assert '최종입원의 퇴원일' in r[26]['conditions']
assert '5%' in r[9]['amount'] and '50%' in r[22]['amount']
assert '간병인사용 일당은 지급하지' not in r[35]['conditions']
assert all('받은인 경우' not in x['target'] for x in r)
print('PASS: 122 rows; 9 headers; identity, created_at and all source cells unchanged; original percentages preserved; diagnosis/renewal/inpatient/care limits verified.')
