import json,zipfile,re,hashlib
from pathlib import Path
from lxml import etree as E
R=Path('work/heungkuk_life');rows=json.loads((R/'records.json').read_text(encoding='utf8'));M=json.loads((R/'manifest.json').read_text(encoding='utf8'))
f=Path('outputs/01a10ed0-eb0e-7720-80fe-23aace7c950b/흥국생명_2507_담보분석.xlsx')
ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
with zipfile.ZipFile(f) as z:
 shared=[]
 if 'xl/sharedStrings.xml' in z.namelist():
  shared=[''.join(x.itertext()) for x in E.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',ns)]
 def val(cell):
  if cell.get('t')=='inlineStr':return ''.join(cell.find('s:is',ns).itertext())
  v=cell.find('s:v',ns)
  if v is None:return ''
  return shared[int(v.text)] if cell.get('t')=='s' else v.text
 data=E.fromstring(z.read('xl/worksheets/sheet1.xml'))
 xr=data.findall('s:sheetData/s:row',ns)
 h=['id','company_name','product_name','coverage_name','coverage_target','coverage_amount','coverage_conditions','created_at','updated_at']
 assert [val(c) for c in xr[0]]==h
 assert len(xr)==len(rows)+1==156
 for rr,record in zip(xr[1:],rows):
  cells={re.sub(r'\d','',c.get('r')):val(c) for c in rr}
  for col,k in zip('ABCDEFGHI',h):assert cells.get(col,'')==str(record[k]),(record['id'],k)
  assert cells['H'].endswith('+09:00') and cells['I'].endswith('+09:00')
 assert data.find('s:tableParts',ns).get('count')=='1'
 assert len([v for v in z.namelist() if re.match(r'xl/worksheets/sheet\d+.xml$',v)])==3
 for name in [v for v in z.namelist() if v.startswith('xl/worksheets/sheet') and v.endswith('.xml')]:
  for c in E.fromstring(z.read(name)).findall('.//s:c',ns):assert c.get('t')!='e',(name,c.get('r'))
for r in rows:
 pages=[int(v) for v in r['source_page'].split('–')];lim=next(x['pages'] for x in M if x['path']==r['source_file']);assert all(1<=v<=lim for v in pages)
assert M[4]['sha256']==M[6]['sha256'] and M[5]['sha256']==M[7]['sha256']
assert len([r for r in rows if '통합암항암약물방사선치료비' in r['coverage_name']])==10
assert len([r for r in rows if r['coverage_name'].startswith('무배당 1~5종재해수술')])==5
assert len(set(r['id'] for r in rows))==155
print('VERIFIED: 155 rows, exact nine columns, 3 sheets, all exported cells, source bounds, duplicate PDF hashes, 10 cancer categories, 5 surgery categories.')
print('SHA256',hashlib.sha256(f.read_bytes()).hexdigest())

