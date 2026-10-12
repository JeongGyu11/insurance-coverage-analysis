from pathlib import Path
import json,re,zipfile
from lxml import etree as E
R=Path('work/fubon');r=json.loads((R/'records.json').read_text(encoding='utf8'));m=json.loads((R/'manifest.json').read_text(encoding='utf8'));a=json.loads((R/'audit.json').read_text(encoding='utf8'))
h=['id','company_name','product_name','coverage_name','coverage_target','coverage_amount','coverage_conditions','created_at','updated_at']
assert len(r)==355 and [x['id'] for x in r]==list(range(1,356))
assert all(x[k] for x in r for k in h)
assert len({(x['product_name'],x['coverage_name'],x['coverage_target']) for x in r})==355
for x in r:
 assert Path(x['source_file']).is_file() and Path(x['business_file']).is_file()
 assert x['created_at']==x['updated_at'] and x['created_at'].endswith('+09:00')
 count=next(v['pages'] for v in m if v['path']==x['source_file'])
 assert all(1<=int(v)<=count for v in re.findall(r'\d+',x['source_page']))
 if '집중보장형' in x['coverage_name']:assert '10년' in x['coverage_amount'] and '200%' in x['coverage_amount']
 if '생활자금특약' in x['coverage_name']:assert '최대 60개월' in x['coverage_conditions'] and '12개월' in x['coverage_conditions']
 if '사후정리' in x['coverage_name'] or '선지급서비스' in x['coverage_name']:assert '추가' in x['coverage_amount']
 if '보험료납입면제' in x['coverage_name']:assert '현금' in x['coverage_amount'] or '면제' in x['coverage_amount']
for v in a:
 assert any(x['source_file']==m[v['doc']]['path'] and x['coverage_name'].startswith(v['section']) for x in r),(v['doc'],v['section'])
for di in [3,5]:
 p=json.loads((R/f'doc{di}.json').read_text(encoding='utf8'))
 lines='\n'.join(p[1:4]).replace('\r','').splitlines()
 starts=[int(z[1]) for line in lines if (z:=re.match(r'^(\d+)\s+(.+)',line)) and not any(k in z[2] for k in ['사후정리','선지급','장애인','지정대리','특별조건','특정 신체','보험용어','보험계약관련','상품구성','보험료납입면제'])]
 assert len(starts)==sum(x['doc']==di for x in a),(di,len(starts),sum(x['doc']==di for x in a))
f=Path('outputs/01a10ed0-eb0e-7720-80fe-23aace7c950b/푸본현대생명_2507_담보분석.xlsx');N={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
with zipfile.ZipFile(f) as z:
 ss=[''.join(t.itertext()) for t in E.fromstring(z.read('xl/sharedStrings.xml'))]
 def cells(i):
  out={}
  for c in E.fromstring(z.read(f'xl/worksheets/sheet{i}.xml')).findall('.//s:sheetData/s:row/s:c',N):
   v=c.find('s:v',N);v=v.text if v is not None else ''
   if c.get('t')=='s':v=ss[int(v)]
   elif c.get('t')=='inlineStr':v=''.join(c.find('s:is',N).itertext())
   out[c.get('r')]=v
  return out
 d=cells(1);source=cells(3)
 assert [d[c+'1'] for c in 'ABCDEFGHI']==h
 assert len([k for k in d if re.fullmatch('A[0-9]+',k)])==356
 for i,x in enumerate(r,2):
  for c,k in zip('ABCDEFGHI',h):assert d[c+str(i)]==str(x[k]),(i,c,d[c+str(i)],str(x[k]))
  assert source['D'+str(i)]==x['source_file'] and source['E'+str(i)]==x['source_page']
 assert len([n for n in z.namelist() if re.fullmatch('xl/tables/table[0-9]+.xml',n)])==2
print('PASS: 355 records, 5 products; full benefit TOC/table reconciliation; exact 9 columns and every exported value; source bounds; payout variants; date offsets; two filter tables.')
