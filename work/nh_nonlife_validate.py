from zipfile import ZipFile
from lxml import etree as E
from pathlib import Path
import json
r=json.loads(Path('work/nh_nonlife/records.json').read_text(encoding='utf8'))
z=ZipFile('outputs/NH농협손해보험_2507_담보분석.xlsx');ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
strings=[]
if 'xl/sharedStrings.xml' in z.namelist():strings=[''.join(x.itertext()) for x in E.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',ns)]
def v(c):
 if c.get('t')=='s':return strings[int(c.find('s:v',ns).text)]
 if c.get('t')=='inlineStr':return ''.join(c.find('s:is',ns).itertext())
 x=c.find('s:v',ns);return x.text if x is not None else ''
t=E.fromstring(z.read('xl/worksheets/sheet1.xml'));cells={c.get('r'):c for c in t.findall('.//s:c',ns)}
h=['id','company_name','product_name','coverage_name','coverage_target','coverage_amount','coverage_conditions','created_at','updated_at']
assert [v(cells[c+'1']) for c in 'ABCDEFGHI']==h
assert len(r)==748 and len({(x['product_name'],x['coverage_name']) for x in r})==748
for i,x in enumerate(r,2):
 for c,k in zip('ABCDEFGHI',h):assert v(cells[f'{c}{i}'])==str(x[k]),(i,k)
 assert all(x[k] for k in h) and '+09:00' in x['created_at']
 assert Path(x['source_file']).is_file()
assert len(t.findall('.//s:row',ns))==749
assert not t.findall('.//s:f',ns)
print('Verified 748 rows, exact 9 columns, all exported values match, timestamps retain timezone, source files exist, no duplicate coverage keys.')

