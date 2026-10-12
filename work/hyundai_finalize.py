import json,re,collections
from pathlib import Path
R=Path('work/hyundai');r=json.loads((R/'records.json').read_text(encoding='utf8'));m=json.loads((R/'manifest.json').read_text(encoding='utf8'))
# Exclusion-only endorsements and a generic medical umbrella do not create new payouts.
r=[x for x in r if not (x['doc'] in [126,129,131,133,136] and ('위험제외' in x['coverage_name'] or ('기본형' in x['coverage_name'] and '실손의료비' in x['coverage_name'])))]
for x in r:
 if x.get('raw'):
  p=x['raw'].get('group','');n=x['raw']['name']
  if p and len(p)>6 and p not in n and not any(t in p for t in ['상해관련','질병관련','기본계약','의무가입','비용손해관련']) and '/' not in x['coverage_name']:
   x['coverage_name']=p+' / '+n
 if '추가 대조' in x['review']:
  x['source_page']='';x['review']+=' 약관 페이지는 확정하지 않아 비워 두었습니다. 상품요약서 지급표 페이지를 우선 확인하십시오.'
 c=x['coverage_conditions']
 if len(c)>900:
  qs=re.split(r'(?<=다\.)\s+',c);unique=[]
  for q in qs:
   q=q.strip()
   if q and q not in unique:unique.append(q)
  ranked=sorted(enumerate(unique),key=lambda z:(0 if any(t in z[1] for t in ['90일','감액','50%','공제','차감','재진단','365일','지급하지','보상하지','연간','한도','8만원','10년']) else 1,z[0]))
  keep=[];length=0
  for i,q in ranked:
   if length+len(q)<=900:keep.append((i,q));length+=len(q)+1
  if keep:x['coverage_conditions']=' '.join(q for i,q in sorted(keep))
  x['review']+=' 지급조건은 핵심 조항 중심으로 요약했으며 전체 제외사항은 원문을 확인하십시오.'
for i,x in enumerate(r,1):x['id']=i
(R/'records.json').write_text(json.dumps(r,ensure_ascii=False),encoding='utf8')
pending=[x['id'] for x in r if '추가 대조' in x['review']]
(R/'pending_ids.json').write_text(json.dumps(pending),encoding='utf8')
print(len(r),'pending',len(pending),'products',len(set(x['product_name'] for x in r)))
print('maxlength',{k:max(len(str(x[k])) for x in r) for k in ['coverage_name','coverage_target','coverage_amount','coverage_conditions']})
assert all(x['company_name'] and x['product_name'] and x['coverage_name'] and x['coverage_amount'] for x in r)
assert not any('해당 특약을 가입한 계약에 적용합니다' in x['coverage_conditions'] for x in r)

