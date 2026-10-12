from zipfile import ZipFile
from lxml import etree as E
from pathlib import Path
import json
r=json.loads(Path('work/lotte/records.json').read_text(encoding='utf8'));z=ZipFile('outputs/롯데손해보험_2507_담보분석.xlsx');ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
strings=[]
if 'xl/sharedStrings.xml' in z.namelist():strings=[''.join(x.itertext()) for x in E.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',ns)]
def v(c):
 if c.get('t')=='s':return strings[int(c.find('s:v',ns).text)]
 if c.get('t')=='inlineStr':return ''.join(c.find('s:is',ns).itertext())
 x=c.find('s:v',ns);return x.text if x is not None else ''
t=E.fromstring(z.read('xl/worksheets/sheet1.xml'));cells={c.get('r'):c for c in t.findall('.//s:c',ns)}
h=['id','company_name','product_name','coverage_name','coverage_target','coverage_amount','coverage_conditions','created_at','updated_at']
assert [v(cells[c+'1']) for c in 'ABCDEFGHI']==h
assert len(r)==79 and len({(x['product_name'],x['coverage_name']) for x in r})==79
for i,x in enumerate(r,2):
 for c,k in zip('ABCDEFGHI',h):assert v(cells[f'{c}{i}'])==str(x[k]),(i,k)
 assert all(x[k] for k in h) and '+09:00' in x['created_at'] and x['id']==i-1
 assert Path(x['summary_file']).is_file() and Path(x['business_file']).is_file()
 if x['source_file']:assert Path(x['source_file']).is_file()
 else:assert x['review'].startswith('확인 필요') and '확인 불가' in x['coverage_amount']
assert len(t.findall('.//s:row',ns))==80
assert not t.findall('.//s:f',ns)
assert len([n for n in z.namelist() if n.startswith('xl/tables/table') and n.endswith('.xml')])==2
assert sum(not x['source_file'] for x in r)==1
print('Verified 79 rows, exact 9 columns, all saved values match, unique keys and IDs, timezone retained, source files exist; 1 summary-only coverage clearly flagged.')
