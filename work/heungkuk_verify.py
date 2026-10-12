from pathlib import Path
import json,re,zipfile
from lxml import etree as E
R=Path('work/heungkuk');r=json.loads((R/'records.json').read_text(encoding='utf8'));m=json.loads((R/'manifest.json').read_text(encoding='utf8'));pending=json.loads((R/'pending_ids.json').read_text(encoding='utf8'))
h=['id','company_name','product_name','coverage_name','coverage_target','coverage_amount','coverage_conditions','created_at','updated_at']
assert len(r)==2240 and [x['id'] for x in r]==list(range(1,len(r)+1))
assert len(set(x['product_name'] for x in r))==15
assert all(x[k] for x in r for k in ['company_name','product_name','coverage_name','coverage_target','coverage_amount'])
assert not any('해당 특약을 가입한 계약에 적용합니다' in x['coverage_conditions'] for x in r)
for x in r:
 assert Path(x['source_file']).is_file() and Path(x['summary_file']).is_file()
 count=next(v['pages'] for v in m if v['path']==x['source_file'])
 assert all(1<=int(v)<=count for v in re.findall(r'\d+',x['source_page']))
 assert x['created_at']==x['updated_at'] and x['created_at'].endswith('+09:00')
 if '잔고' in x['coverage_amount']:assert '월렛' in x['coverage_name']
 if '납기후2배보장' in x['coverage_name']:assert '150%' in x['coverage_amount'] and '200%' in x['coverage_amount']
 assert max(len(x[k]) for k in h if isinstance(x[k],str))<32767
N={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
f=Path('outputs/01a10ed0-eb0e-7720-80fe-23aace7c950b/흥국화재_2507_담보분석.xlsx')
with zipfile.ZipFile(f) as z:
 ss=[''.join(x.itertext()) for x in E.fromstring(z.read('xl/sharedStrings.xml'))]
 def cells(i):
  d={}
  for c in E.fromstring(z.read(f'xl/worksheets/sheet{i}.xml')).findall('.//s:sheetData/s:row/s:c',N):
   v=c.find('s:v',N);v=v.text if v is not None else ''
   if c.get('t')=='s':v=ss[int(v)]
   elif c.get('t')=='inlineStr':v=''.join(c.find('s:is',N).itertext())
   d[c.get('r')]=v
  return d
 d=cells(1);s=cells(2);src=cells(3)
 assert [d[c+'1'] for c in 'ABCDEFGHI']==h
 for i,x in enumerate(r,2):
  for c,k in zip('ABCDEFGHI',h):assert d.get(c+str(i),'')==str(x[k]),(i,c,d.get(c+str(i)),x[k])
  assert src['D'+str(i)]==x['source_file'] and src['E'+str(i)]==x['source_page']
 assert int(s['B23'])==len(r) and int(s['B25'])==len(pending)
 assert len([n for n in z.namelist() if re.fullmatch('xl/tables/table[0-9]+.xml',n)])==3
print('PASS',len(r),'rows; 15 payout products; all exported values; 9 columns; source page bounds; timestamps; wallet isolation; maturity and medical amounts; review items',len(pending))
print('MAX LENGTHS',[(k,max(len(x[k]) for x in r)) for k in h[3:7]])

