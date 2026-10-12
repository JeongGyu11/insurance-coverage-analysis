import json,re,unicodedata
from pathlib import Path
R=Path('work/heungkuk');r=json.loads((R/'records.json').read_text(encoding='utf8'));S=json.loads((R/'sections.json').read_text(encoding='utf8'));M=json.loads((R/'manifest.json').read_text(encoding='utf8'))
def stem(s):
 s=unicodedata.normalize('NFKC',s);s=re.sub(r'\([^()]*\)','',s)
 s=re.sub(r'\([^()]*\)','',s);s=re.sub(r'[^가-힣A-Za-z0-9]','',s).replace('보험료납입면제대상보장','보험료납입면제대상').removeprefix('무')
 return s
pending=[]
for x in r:
 if not x['source_page']:
  di=next(int(m['key'][3:]) for m in M if m['path']==x['source_file']);n=x['coverage_name'].rstrip(',');x['coverage_name']=n
  candidates=[s for s in S.get(str(di),[]) if any(stem(n)==stem(v) for v in s['aliases'])]
  if candidates:
   s=min(candidates,key=lambda s:abs(len(n)-len(s['name'])));x['source_page']=f'{s["start"]}–{s["end"]}';x['review']='약관과 상품요약서의 담보명 표기 차이 대조. 요약서에 명시된 지급형·한도·감액 구분을 유지.'
  else:
   x['review']='상품요약서 지급표에 명시된 담보. 약관 내 같은 제목을 추가 대조할 필요가 있어 약관 조건을 추정하지 않음.';pending.append(x['id'])
  if '실제가입한계약' in re.sub(r'\s','',x['coverage_conditions']):raise ValueError('filler')
 # explain payout units in ordinary Korean
 x['coverage_amount']=x['coverage_amount'].replace('가입금액를','가입금액을').replace('장해지급률를','장해지급률을').replace('×장해지급률',' × 장해지급률')
 if x['raw'] and '납기후2배보장' in x['coverage_name']:
  x['coverage_amount']='계약의 보장보험료 납입기간 50% 경과 전에는 해당 가입금액의 100%, 50% 경과 후 납입완료 전에는 150%, 납입완료 후에는 200%를 적용합니다. '+x['coverage_amount']
 if '중대한화상및부식' in x['coverage_name']:x['coverage_target']+=' 중대한 화상·부식은 표준 신체표면적 측정법상 최소 20% 이상의 3도 화상 또는 화학약품 등에 의한 부식을 말합니다.'
 if '일반상해' in x['coverage_name'] and '후유장해' in x['coverage_name']:
  x['coverage_target']=x['coverage_target'].replace('피보험자가 상해로','피보험자가 급격하고 우연한 외래의 사고로 입은 상해로')
 if '유사암' in x['coverage_name'] and all(v not in x['coverage_target'] for v in ['갑상선암','기타피부암']):
  x['coverage_target']+=' 이 상품의 유사암 구분은 기타피부암·갑상선암·제자리암·경계성종양이며 유사암제외 담보에서는 이 질환을 별도 담보로 구분합니다.'
 if '(2종)' in x['product_name'] and x['raw'] and '1년미만50%' in re.sub(r'\s','',x['coverage_conditions']):x['coverage_conditions']+=' 초기 감액기간은 최초계약 기준이며 갱신계약에서 같은 기간을 새로 기산하지 않습니다.'
# maturity refunds only for explicitly described type 1 savings portions of the two healthy products
stamp=r[0]['created_at']
for di in [25,28]:
 p=json.loads((R/f'doc{di}.json').read_text(encoding='utf8'));hits=[i+1 for i,t in enumerate(p) if '만기환급금의 지급' in t and '산출방법서' in t];page=next((i for i in hits if 60<i<100),None)
 if page:
  base=next(v for v in r if v['source_file']==M[di]['path']);x={k:base[k] for k in base};x.update(id=len(r)+1,coverage_name='기본계약 적립부분 / 만기환급금(1종)',coverage_target='1종 해약환급금지급형의 적립부분을 가진 계약이 보험기간 만기까지 유지된 경우의 보험수익자.',coverage_amount='보험료 및 해약환급금 산출방법서에 따라 계산한 적립부분 만기환급금. 공시이율에 연동하므로 고정 원화액이 아니며 약관상 최저보증이율은 연복리 0.3%.',coverage_conditions='1종의 적립부분에 해당하며 적립부분이 없는 2종 순수보장형에는 지급하지 않습니다. 자동대출납입 보험료·이자와 보험계약대출 원리금이 있으면 차감합니다.',source_page=str(page),summary_page='1–'+str(M[di-1]['pages']),review='보통약관 만기환급금 지급과 상품요약서의 1종 적립부분·최저보증이율 대조.',raw=None);r.append(x)
for i,x in enumerate(r,1):x['id']=i
(R/'records.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');(R/'pending_ids.json').write_text(json.dumps(pending),encoding='utf8')
print('ROWS',len(r),'PENDING',len(pending));print([(x['id'],x['coverage_name']) for x in r if x['id'] in pending][:50])

