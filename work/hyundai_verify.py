import json,zipfile,re,hashlib
from pathlib import Path
from lxml import etree as E
R=Path('work/hyundai');rows=json.loads((R/'records.json').read_text(encoding='utf8'));M=json.loads((R/'manifest.json').read_text(encoding='utf8'))
f=Path('outputs/01a10ed0-eb0e-7720-80fe-23aace7c950b/현대해상_2507_담보분석.xlsx')
ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
with zipfile.ZipFile(f) as z:
 shared=[]
 if 'xl/sharedStrings.xml' in z.namelist():shared=[''.join(x.itertext()) for x in E.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',ns)]
 def val(c):
  if c.get('t')=='inlineStr':return ''.join(c.find('s:is',ns).itertext())
  v=c.find('s:v',ns)
  return '' if v is None else shared[int(v.text)] if c.get('t')=='s' else v.text
 data=E.fromstring(z.read('xl/worksheets/sheet1.xml'));xr=data.findall('s:sheetData/s:row',ns)
 h=['id','company_name','product_name','coverage_name','coverage_target','coverage_amount','coverage_conditions','created_at','updated_at']
 assert [val(c) for c in xr[0]]==h
 assert len(xr)==len(rows)+1
 for rr,record in zip(xr[1:],rows):
  cells={re.sub(r'\d','',c.get('r')):val(c) for c in rr}
  for col,k in zip('ABCDEFGHI',h):assert cells.get(col,'')==str(record[k]),(record['id'],k,cells.get(col))
  assert cells['H'].endswith('+09:00')
 sheets=[v for v in z.namelist() if re.match(r'xl/worksheets/sheet\d+.xml$',v)]
 assert len(sheets)==4
 for n in sheets:
  for c in E.fromstring(z.read(n)).findall('.//s:c',ns):assert c.get('t')!='e'
 pending=E.fromstring(z.read('xl/worksheets/sheet4.xml')).findall('s:sheetData/s:row',ns)
 assert len(pending)==412
for r in rows:
 if r['source_page']:
  lim=next(x['pages'] for x in M if x['path']==r['source_file'])
  assert all(1<=int(v)<=lim for v in r['source_page'].split('–')),(r['id'],r['source_page'],lim)
 assert '해당 특약을 가입한 계약에 적용합니다' not in r['coverage_conditions']
assert [r['id'] for r in rows]==list(range(1,len(rows)+1))
print('VERIFIED',len(rows),'exact nine columns, four sheets, 411 pending, source page bounds and all exported cell values')
print('SHA256',hashlib.sha256(f.read_bytes()).hexdigest())

