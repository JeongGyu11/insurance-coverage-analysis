import json,re
from pathlib import Path
R=Path('work/heungkuk');r=json.loads((R/'records.json').read_text(encoding='utf8'));S=json.loads((R/'sections.json').read_text(encoding='utf8'));M=json.loads((R/'manifest.json').read_text(encoding='utf8'));pending=[]
def cleanname(n):
 n=n.replace('상해일반상해','일반상해').replace('상해및질병보험료','보험료').replace('기타가족','가족').removeprefix('및')
 n=n.replace('일반입원비(상급종합병원)','일반상해입원비(상급종합병원)').replace('사용일반질병입원비','사용질병입원비')
 n=n.replace('(1일-150일(','(1일-150일)(')
 return n
def core(n):
 n=re.sub(r'\([^()]*(?:\([^()]*\)[^()]*)*\)','',n)
 return re.sub(r'[^가-힣A-Za-z0-9]','',n)
for x in r:
 x['coverage_name']=cleanname(x['coverage_name'])
 if not x['source_page']:
  di=next(int(m['key'][3:]) for m in M if m['path']==x['source_file']);n=core(x['coverage_name'])
  matches=[s for s in S.get(str(di),[]) if any(core(v)==n for v in s['aliases'])]
  if matches:
   # restrict hospital-specific wording when source captions include an institution
   institution=next((v for v in ['상급종합병원','종합병원','요양병원'] if v in x['coverage_name']),'')
   special=[s for s in matches if institution in s['name']] if institution else matches
   s=(special or matches)[0];x['source_page']=f'{s["start"]}–{s["end"]}';x['review']='요약서·약관의 담보명 표기 차이를 대조. 지급금액과 가입형 구분은 해당 상품요약서 지급표를 유지.'
  else:
   # use summary as the actual source, without a guessed broad policy page range
   x['policy_file']=x['source_file'];x['source_file']=x['summary_file'];x['source_page']=x['summary_page'];x['review']='상품요약서 지급표에 근거해 작성. 같은 약관 제목의 추가 대조가 필요한 항목; 임의로 다른 특약의 조건을 적용하지 않음.';pending.append(x['id'])
 if x['coverage_conditions']=='보험기간 중 위 지급사유가 발생해야 합니다. 해당 보장의 진단·치료·사고 범위에 따라 지급합니다.':x['coverage_conditions']=''
 if '(2종)' in x['product_name'] and '(갱신형' not in x['coverage_name']:x['review']+=' 상품 종별(2종)은 갱신형으로 상품명에서 구분.'
# final exact duplicate comparison after name normalization
out=[];seen=set()
for x in r:
 k=(x['product_name'],x['coverage_name'],x['coverage_target'],x['coverage_amount'])
 if k not in seen:seen.add(k);out.append(x)
for i,x in enumerate(out,1):x['id']=i
pending=[x['id'] for x in out if x.get('policy_file')]
(R/'records.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');(R/'pending_ids.json').write_text(json.dumps(pending),encoding='utf8')
print(len(out),'summary source review',len(pending))

