import json,re,zipfile
from pathlib import Path
from lxml import etree as E
p=Path('work/mirae');r=json.loads((p/'records.json').read_text(encoding='utf8'));s=json.loads((p/'sections.json').read_text(encoding='utf8'));m=json.loads((p/'manifest.json').read_text(encoding='utf8'));h=['id','company_name','product_name','coverage_name','coverage_target','coverage_amount','coverage_conditions','created_at','updated_at']
assert len(r)==230 and [x['id'] for x in r]==list(range(1,231))
assert len({(x['product_name'],x['coverage_name']) for x in r})==230
assert all(x[k] for x in r for k in h)
assert all(x['company_name']=='미래에셋생명' for x in r)
health=[x for x in r if x['product_name'].startswith('M-케어')]
assert len(health)==196
assert {x['source_name'] for x in health}=={x['name'] for x in s['doc2'] if x['start']<977}
assert all(Path(x['source_file']).is_file() and Path(x['summary_file']).is_file() and Path(x['business_file']).is_file() for x in r)
assert all(re.search(r'\+09:00$',x['created_at']) for x in r)
assert all(len(x['coverage_conditions'])<2000 for x in r)
for x in r:
 if '바늘생검' in x['coverage_name'] or '6대질병진단 검사비' in x['coverage_name']:
  assert '연간 1회' in x['coverage_conditions'] and '최초 1회' not in x['coverage_conditions']
 if '다빈치' in x['coverage_name']:assert '25%' in x['coverage_amount'] and '180일' in x['coverage_amount']
 if '월지급 치료지원특약' in x['coverage_name']:assert '36회' in x['coverage_amount'] and '120회' in x['coverage_amount']
 if '가입형)' in x['coverage_name'] and '경영인을 위한 정기보험' in x['coverage_name']:assert '10%' in x['coverage_amount'] and '−9' in x['coverage_amount']
N={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
file=Path('outputs/01a10ed0-eb0e-7720-80fe-23aace7c950b/미래에셋생명_2507_담보분석.xlsx')
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
 d=cells(1);summary=cells(2);sources=cells(3)
 assert [d[c+'1'] for c in 'ABCDEFGHI']==h
 assert len([k for k in d if re.fullmatch('A[0-9]+',k)])==231
 for i,x in enumerate(r,2):
  for c,k in zip('ABCDEFGHI',h):assert d[c+str(i)]==str(x[k]),(i,c)
  assert sources['F'+str(i)]==x['source_file'] and sources['G'+str(i)]==x['source_page']
 assert summary['B5']=='196' and summary['B6']=='23' and summary['B7']=='11' and summary['B9']=='230'
 assert len([n for n in z.namelist() if re.fullmatch('xl/tables/table[0-9]+.xml',n)])==2
 assert not any(v.startswith(('#REF!','#DIV/0!','#VALUE!','#NAME?')) for v in d.values())
old=json.loads((p/'records_before_detail_revision.json').read_text(encoding='utf8'))
for i,x in enumerate(r[:229]):assert x['created_at']==old[i]['created_at'] and x['updated_at']!=old[i]['updated_at']
for x in r:
 if '요로결석 진단' in x['coverage_name']:assert '1년이 지난 다음 날' in x['coverage_conditions']
 if x['source_page'].startswith('779–'):assert '365일' in x['coverage_conditions'] and '지방종' in x['coverage_conditions']
 if x['source_page'].startswith('73–'):assert '세부보장' in x['coverage_amount'] and '예로는' in x['coverage_target']
 assert '이 행의 지급사유' not in x['coverage_conditions']
assert '연금개시 전 사망' in r[-1]['coverage_name']
print('PASS: 230 rows; 196/23/11 per product; nine headers; every saved value matches; source links; uniqueness; preserved creation timestamps; surgery code/365-day exception, urolithiasis waiting, added annuity death benefit; two tables.')
