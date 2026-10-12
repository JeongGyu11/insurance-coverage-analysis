from zipfile import ZipFile
from lxml import etree as E
from pathlib import Path
import json,collections
file=Path('outputs/ABL생명_2507_담보분석.xlsx')
z=ZipFile(file);ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
strings=[]
if 'xl/sharedStrings.xml' in z.namelist():
 strings=[''.join(x.itertext()) for x in E.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',ns)]
def val(cell):
 if cell is None:return None
 t=cell.get('t');v=cell.find('s:v',ns)
 if t=='s':return strings[int(v.text)]
 if t=='inlineStr':return ''.join(cell.find('s:is',ns).itertext())
 return v.text if v is not None else None
s=E.fromstring(z.read('xl/worksheets/sheet1.xml'));cells={a.get('r'):a for a in s.findall('.//s:c',ns)}
r=json.loads(Path('work/records.json').read_text(encoding='utf8'))
headers=[val(cells[f'{c}1']) for c in 'ABCDEFGHI']
assert headers==['id','company_name','product_name','coverage_name','coverage_target','coverage_amount','coverage_conditions','created_at','updated_at']
for i,x in enumerate(r,2):
 assert val(cells[f'A{i}'])==str(x['id'])
 for c in 'BCD':assert val(cells[f'{c}{i}'])
 assert val(cells[f'G{i}'])==x['conditions'],(i,'condition changed')
 ts=val(cells[f'H{i}']);assert '+09:00' in ts,(i,ts)
 assert len(val(cells[f'F{i}']) or '')<32767
print('headers',headers,'rows',len(r),'required blanks',0,'condition roundtrip','exact')
print('time',val(cells['H2']),cells['H2'].get('t'))
print('product rows',dict(collections.Counter(x['doc'] for x in r)))
print('tables',[n for n in z.namelist() if n.startswith('xl/tables/') and n.endswith('.xml')])
print('timestamp XML',E.tostring(cells['H2'],encoding='unicode')[:450])
