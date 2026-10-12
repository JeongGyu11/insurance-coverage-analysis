# Build final rows from the reviewed data; use only same medical title or explicit parent title.
import json,re,copy,collections
from pathlib import Path
R=Path('work/hyundai')
source=Path('work/hyundai_records.py').read_text(encoding='utf-8-sig')
exec(source.split('for b in benefits:')[0])
def pagehits(di,term,minpage=15):
 return [i+1 for i,t in enumerate(P[di]) if co(term) in co(t) and i+1>=minpage]
records=json.loads((R/'records.json').read_text(encoding='utf8'))
def scopekey(s):
 s=co(s)
 for term in ['(간편건강고지)','(간편맞춤고지)','(갱신형)','[맞춤고지Ⅰ]','[맞춤고지Ⅱ]','(연간1회한)','(연간1회한,급여)','(급여)','(전환용)']:
  s=s.replace(term,'')
 return canon(s)
scope={di:collections.defaultdict(list) for di in lookup}
for di in scope:
 for sec in S.get(str(di),[]):
  for v in sec['aliases']:scope[di][scopekey(v)].append(sec)
changed=0
for r in records:
 if not r['raw']:continue
 b=r['raw'];di=r['doc'];sec,score=sectionmatch(di,b['name'],b.get('group',''))
 if not sec and '추가 대조' in r['review']:
  tests=[b['name'],b.get('group',''),*aliases(b.get('group',''))]
  candidates=[]
  for t in tests:candidates+=scope[di].get(scopekey(t),[])
  candidates=list({s['start']:s for s in candidates}.values())
  if len(candidates)==1:sec=candidates[0];score=.98
 if sec:
  if '추가 대조' in r['review']:
   cc,defs=clauses(sec,b['name'],b['cause'],b['amount'])
   tableconds=[v.strip('()')+'.' for v in re.findall(r'\([^)]*(?:최초|각각|회한|한도|미만|일이상|이상경과)[^)]*\)',b['cause']+' '+b['amount'])]
   r['coverage_conditions']=' '.join(dict.fromkeys(tableconds+cc))
   r['source_page']=f'{sec["start"]}–{sec["end"]}';r['review']='상품요약서와 같은 담보 또는 같은 세부보장의 상위 특약 조문을 대조. 괄호·갱신·고지 표기는 원문 구분 유지.';changed+=1
  # Give subgroup rows a complete coverage name.
  parent=b.get('group','')
  if parent and len(co(parent))>6 and co(parent) not in co(b['name']):
   pa=aliases(parent);parentdisplay=pa[0]
   if len(pa)>1 and '갱신형' in pa[-1] and '갱신형' not in pa[0]:parentdisplay+='(갱신형 포함)'
   if not any(v in co(parentdisplay) for v in ['상해관련','질병관련','비용손해관련','기본계약','의무가입']):r['coverage_name']=parentdisplay+' / '+b['name']
 # Keep only operative source content and make conditions concise.
 cn=r['coverage_name'];bc=co(sec['body']) if sec else ''
 cond=r['coverage_conditions']
 cond=re.sub(r'\(이하[^)]*\)','',cond)
 # Drop repeated payout events from conditions, keeping limits in amount and timing/deductions here.
 pieces=re.split(r'(?<=다\.)\s+',cond);kept=[]
 for q in pieces:
  qq=co(q)
  if not qq:continue
  if any(v in qq for v in ['합의하지못','제3자','예시안내','판정에드는의료비용','계약자적립액','보통약관을따','회사는피보험자가']) and not any(v in qq for v in ['감액','공제','차감','90일','최초계약','보장개시']):continue
  if any(qq==co(v) or (len(qq)>30 and qq in co(v)) for v in kept):continue
  kept.append(clean(q))
 cond=' '.join(kept)
 if len(cond)>850:
  # Keep each meaningful limit once and omit general impairment discussion.
  important=[q for q in kept if any(v in co(q) for v in ['최초계약','90일','감액','공제','차감','연간','한도','50%','1년','지급기간','365일','전이','재진단','180일','기지급'])]
  concisecond=' '.join(important)
  if concisecond:cond=concisecond
 if '후유장해' in cn and len(cond)>700:
  first='장해분류표에 따라 판정합니다. 같은 상해·질병의 장해는 합산하되 같은 부위의 중복 장해는 높은 지급률을 적용하고 기지급 장해가 악화되면 기지급분을 차감합니다.'
  cond=first+(' 180일 이내 확정되지 않으면 180일째 의사진단에 따른 고정 상태를 기준으로 하되 장해별 별도 판정시기는 그 기준을 따릅니다.' if '180일' in bc else '')
  # A monthly/threshold-specific table retains its payout guarantee and duration in amount.
 if '간병인사용' in cn and '8만원' in co(r['coverage_amount']):
  cond+=' 간병인 평균 사용금액이 1일 8만원 미만이면 병원(요양병원 제외) 사용급여는 정상금액의 50%입니다. 요양병원·의원 및 간호·간병통합서비스 급여는 각각의 지급구분을 적용합니다.'
 r['coverage_conditions']=clean(cond)
 # Clarify example amounts instead of presenting them as fixed actual insurance amounts.
 if r['raw'] and '<보험가입금액' in co(r['raw']['amount']):
  r['coverage_amount']+=' 지급표의 원화금액은 표시된 기준 가입금액의 예시이며 실제 지급액은 계약의 해당 가입금액에 지급비율을 적용합니다.'
 if r['raw'] and '각세부보장가입금액' in co(r['raw']['amount']):
  r['coverage_amount']='해당 암의 세부보장별 계약 가입금액 100%, 최초계약 1년 미만에는 50%. 세부보장별 최초 1회 지급하며 각 암의 가입금액은 계약마다 다를 수 있습니다.'
 # Full medical and travel units have explicit supplied-source percentage proof.
 r['coverage_target']=r['coverage_target'].replace('피보험자가 피보험자','피보험자').replace('보험계약자 또는 보험수익자에 지급합니다','')
# Complete travel medical components found in native standard indemnity appendices.
for di in sorted(travel):
 si=next((i for i,m in enumerate(M) if m['product']==M[di]['product'] and m['kind']=='상품요약서'),None)
 for risk in ['상해','질병']:
  hits=pagehits(di,'상급병실료차액');ps=min(hits) if hits else 1;pe=max(hits) if hits else 80
  add(di,risk+' 국내 비급여 상급병실료 차액','해외여행·체류기간에 발생한 '+risk+'로 국내 의료기관에 입원하여 실제 부담한 기준병실과 상급병실의 비급여 병실료 차액.','병실료 차액의 50%, 1일 평균 10만원 한도. 해당 비급여 실손 담보의 연간 가입금액 한도에서 지급합니다.','1일 평균 금액은 전체 상급병실료 차액을 전체 입원일수로 나누어 계산합니다. 중복 실손계약은 비례분담합니다.',ps,pe,si,'전체')
 for nm,limit,counts in [('도수치료·체외충격파치료·증식치료','350만원','50회'),('비급여 주사료','250만원','50회'),('비급여 MRI·MRA','300만원','금액 한도')]:
  hits=pagehits(di,limit);ps=min(hits) if hits else 1;pe=max(hits) if hits else 80
  add(di,'국내 3대 비급여 / '+nm,'해외여행·체류기간에 발생한 상해·질병 치료를 위해 국내 의료기관에서 실제 부담한 '+nm+' 비용.','1회 치료·검사 비용에서 3만원과 보장대상 비용의 30% 중 큰 금액을 공제. 계약일부터 매 1년간 '+limit+' 및 '+counts+' 한도.','중복 실손계약은 비례분담합니다.'+(' 최초 10회 후 객관적 검사결과상 증상 개선·병변 호전이 확인되어야 10회 단위로 연간 한도까지 보장합니다.' if '도수' in nm else ''),ps,pe,si,'전체')
# Administrative-only standalone folders are disclosed in processing status, without invented coverage.
seen=set();final=[]
for r in records:
 k=tuple(r[x] for x in ['product_name','coverage_name','coverage_target','coverage_amount'])
 if k in seen:continue
 seen.add(k);final.append(r)
for i,r in enumerate(final,1):r['id']=i
pending=[r['id'] for r in final if '추가 대조' in r['review']]
(R/'records.json').write_text(json.dumps(final,ensure_ascii=False,indent=2),encoding='utf8')
(R/'pending_ids.json').write_text(json.dumps(pending),encoding='utf8')
print('FINAL',len(final),'RESOLVED',changed,'PENDING',len(pending))
print('PENDING UNIQUE',len(set((r['doc'],r['coverage_name']) for r in final if r['id'] in pending)))
print('LONG CONDITIONS',len([r for r in final if len(r['coverage_conditions'])>1200]))


