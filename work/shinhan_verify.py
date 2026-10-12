from pathlib import Path
import json,re,zipfile
from lxml import etree as E
p=Path('work/shinhan');r=json.loads((p/'records.json').read_text(encoding='utf8'));m=json.loads((p/'manifest.json').read_text(encoding='utf8'))
h=['id','company_name','product_name','coverage_name','coverage_target','coverage_amount','coverage_conditions','created_at','updated_at']
assert len(r)==25 and [x['id'] for x in r]==list(range(1,26))
assert len({(x['product_name'],x['coverage_name']) for x in r})==25
assert all(x[k] for x in r for k in h)
assert [sum(x['product_name']==n for x in r) for n in dict.fromkeys(x['product_name'] for x in r)]==[8,8,9]
for x in r:
 assert Path(x['source_file']).is_file() and Path(x['business_file']).is_file()
 assert x['company_name']=='신한라이프' and x['created_at']==x['updated_at'] and x['created_at'].endswith('+09:00')
 for fkey,pkey in [('source_file','source_page'),('business_file','business_page')]:
  count=next(a['pages'] for a in m if a['path']==x[fkey]);assert all(1<=int(n)<=count for n in re.findall(r'\d+',x[pkey]))
 if '달러' in x['product_name']:assert 'US$' in x['coverage_amount']
 if '생활자금(생활자금형)'==x['coverage_name']:assert '120' in x['coverage_amount'] and '만 1개월' in x['coverage_target']
 if '100세연금형)'==x['coverage_name'][-8:]:assert '99세' in x['coverage_conditions']
 # 수치표를 원문의 성별 지급률과 독립 대조한다.
 if x['coverage_name'].startswith('금리연동연금'):
  main=json.loads((p/'doc3.json').read_text(encoding='utf8'))
  source=main[33] if '100세연금형' in x['coverage_name'] else main[34]
  pairs=re.findall(r'(?:\d+세이상\s*(?:\d+세미만)?)\s+(\d+\.\d+)%\s+(\d+\.\d+)%',source)
  assert len(pairs)==6
  for male,female in pairs:assert f'남 {float(male):.2f}%·여 {float(female):.2f}%' in x['coverage_amount']
  assert '55년 이상 40%' in x['coverage_amount'] and '25년 미만 0%' in x['coverage_amount']
 if '고도재해장해' in x['coverage_name']:assert '정액' in x['coverage_amount'] and '최초 1회' in x['coverage_conditions']
file=Path('outputs/01a10ed0-eb0e-7720-80fe-23aace7c950b/신한라이프_2507_담보분석.xlsx');N={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
with zipfile.ZipFile(file) as z:
 ss=[''.join(t.itertext()) for t in E.fromstring(z.read('xl/sharedStrings.xml'))]
 def cells(i):
  out={}
  for c in E.fromstring(z.read(f'xl/worksheets/sheet{i}.xml')).findall('.//s:sheetData/s:row/s:c',N):
   v=c.find('s:v',N);v=v.text if v is not None else ''
   if c.get('t')=='s':v=ss[int(v)]
   elif c.get('t')=='inlineStr':v=''.join(c.find('s:is',N).itertext())
   out[c.get('r')]=v
  return out
 d=cells(1);s=cells(2);sources=cells(3)
 assert [d[c+'1'] for c in 'ABCDEFGHI']==h
 assert len([k for k in d if re.fullmatch('A[0-9]+',k)])==26
 for i,x in enumerate(r,2):
  for c,k in zip('ABCDEFGHI',h):assert d[c+str(i)]==str(x[k]),(i,c)
  assert sources['D'+str(i)]==x['source_file'] and sources['E'+str(i)]==x['source_page']
 assert [s['B'+str(i)] for i in [5,6,7,8,10]]==['8','8','9','0','25']
 assert len([n for n in z.namelist() if re.fullmatch('xl/tables/table[0-9]+.xml',n)])==2
 assert not any(v.startswith(('#REF!','#DIV/0!','#VALUE!','#NAME?')) for v in d.values())
print('PASS: 25 rows; 8/8/9; exact nine columns and every exported value; source file/page bounds; USD amounts; native source male/female rate pairs; dates; two tables; zero-row administrative material documented.')
