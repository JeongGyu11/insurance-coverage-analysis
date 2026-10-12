from zipfile import ZipFile
from lxml import etree as E
from pathlib import Path
import json,collections
r=json.loads(Path('work/aig/records.json').read_text(encoding='utf8'));z=ZipFile('outputs/AIG손해보험_2507_담보분석.xlsx');ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
strings=[]
if 'xl/sharedStrings.xml' in z.namelist():strings=[''.join(x.itertext()) for x in E.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',ns)]
def v(c):
 if c.get('t')=='s':return strings[int(c.find('s:v',ns).text)]
 if c.get('t')=='inlineStr':return ''.join(c.find('s:is',ns).itertext())
 x=c.find('s:v',ns);return x.text if x is not None else ''
tree=E.fromstring(z.read('xl/worksheets/sheet1.xml'));cells={c.get('r'):c for c in tree.findall('.//s:c',ns)}
assert [v(cells[c+'1']) for c in 'ABCDEFGHI']==['id','company_name','product_name','coverage_name','coverage_target','coverage_amount','coverage_conditions','created_at','updated_at']
assert collections.Counter(x['doc'] for x in r)=={0:40,1:41,2:41}
assert len({(x['product'],x['name']) for x in r})==122
for i,x in enumerate(r,2):
 assert v(cells[f'A{i}'])==str(x['id'])
 assert v(cells[f'B{i}'])=='AIG손해보험'
 for c,field in [('C','product'),('D','name'),('E','target'),('F','amount'),('G','conditions'),('H','created_at'),('I','updated_at')]:assert v(cells[f'{c}{i}'])==x[field],(i,field)
 assert '+09:00' in v(cells[f'H{i}'])
 assert 1<=x['policy_start']<=x['policy_end']<=146
 assert Path(x['summary_path']).is_file() and Path(x['policy_path']).is_file()
assert not tree.findall('.//s:f',ns)
print('Verified 122 rows; 9 columns; required fields populated; no duplicate product-benefit keys; all fields exact after export; source files exist.')
