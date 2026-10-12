import json,re,unicodedata,difflib,collections
from pathlib import Path
from datetime import datetime,timezone,timedelta
R=Path('work/hyundai');M=json.loads((R/'manifest.json').read_text(encoding='utf8'));S=json.loads((R/'sections.json').read_text(encoding='utf8'));T=json.loads((R/'tables.json').read_text(encoding='utf8'))
P={i:json.loads((R/f'doc{i}.json').read_text(encoding='utf8')) for i,m in enumerate(M) if m['kind']=='약관'}
def co(s):return re.sub(r'[\s\ufffe\x00\uf000-\uf8ff]','',s or '')
def clean(s):
 s=re.sub(r'[\s\ufffe\x00\uf000-\uf8ff]+',' ',s or '').strip()
 for word in ['피보험자','보험가입금액','보험기간','보험금','특약가입금액','진단확정','보장개시일','특별약관','후유장해','장해지급률','직접적인','최초','상급종합병원','종합병원','요양병원','기타피부암','갑상선암','제자리암','경계성종양','자기부담금','보상한도','연간','수술분류표','간호ㆍ간병통합서비스','간병인','특약','감액','지급률','중대한','원발암','면제','재해']:
  s=re.sub(r'\s*'.join(re.escape(ch) for ch in word),word,s)
 return s
def canon(s):
 s=unicodedata.normalize('NFKC',co(s)).replace('ㆍ','·').replace('⁀','(').replace('‿',')')
 s=re.sub(r'^.*?다\.','',s)
 s=re.sub(r'^\d+(?:-\d+)*\.?','',s)
 return re.sub(r'[^가-힣A-Za-z0-9]','',s.replace('특별약관','').replace('보장','').replace('허가치료비','허가치료').replace('항바이러스제치료비','항바이러스제치료').replace('전환용',''))
CP={i:[canon(t) for t in p] for i,p in P.items()}
# Header normalization is used only for exact matching; clinical terms remain unchanged.
for di,secs in S.items():
 for sec in secs:
  sec['aliases']=list(dict.fromkeys(canon(v) for v in sec['aliases'] if v))
lookup={int(di):{canon(v):sec for sec in secs for v in sec['aliases']} for di,secs in S.items()}
stamp=datetime.now(timezone(timedelta(hours=9))).isoformat(sep=' ',timespec='seconds');records=[];issues=[];benefits=[]
def add(di,name,target,amount,conditions,ps,pe,si=None,sp='',review='약관 담보별 지급사유·금액 기준·핵심 지급조건 대조.',raw=None):
 product=re.sub(r'^판매완료__\d+_','',M[di]['product']).replace('_',' ')
 records.append(dict(id=len(records)+1,company_name='현대해상',product_name=product,coverage_name=clean(name),coverage_target=clean(target),coverage_amount=clean(amount),coverage_conditions=clean(conditions),created_at=stamp,updated_at=stamp,source_file=M[di]['path'],source_page=f'{ps}–{pe}' if ps!=pe else str(ps),summary_file=M[si]['path'] if si is not None else '',summary_page=str(sp),review=review,raw=raw,doc=di))
def aliases(name):
 n=co(name)
 if len(n)<22:return [n]
 prefix=n[:min(10,len(n)//3)];starts=[z.start() for z in re.finditer(re.escape(prefix),n)]
 if len(starts)>1 and starts[1]>=15:
  return [n[a:b] for a,b in zip(starts,starts[1:]+[len(n)])]
 return [n]
def sectionmatch(di,n,parent=''):
 for test in [n,parent,*aliases(parent)]:
  if canon(test) in lookup.get(di,{}):return lookup[di][canon(test)],1
 # Match an explicitly nested benefit to its parent name; never guess a different medical event.
 scores=[]
 for sec in S.get(str(di),[]):
  for v in sec['aliases']:
   if v and len(v)>7 and canon(n).startswith(v):
    scores.append((len(v),sec))
 if scores:return max(scores,key=lambda v:v[0])[1],.99
 return None,0
# Parse table rows with per-table carried name and per-slot page continuation.
lastslot={};medical={20,23,26,29,32,120};motor={i for i,m in enumerate(M) if m['kind']=='약관' and '자동차보험' in m['product']};travel={126,129,131,133,136}
for tab in T:
 si=tab['doc'];di=next(i for i,m in enumerate(M) if m['product']==M[si]['product'] and m['kind']=='약관')
 if di in medical|motor|travel:continue
 ci,ai=tab['ci'],tab['ai'];slot=(si,round(tab['bbox'][0]/150));prev=lastslot.get(slot)
 current='';group='';carrycause='';carryamount=''
 for ri,row in enumerate(tab['rows'][tab['header']+1:]):
  if len(row)<=ai:continue
  left=[clean(v) for v in row[:ci]];non=[v for v in left if v]
  name=non[-1] if non else ''
  if name:
   current=name
   if len(non)>1 and co(non[0]) not in ['기본계약','의무가입특약','상해관련보장특약','질병관련보장특약','비용손해관련보장특약','상해및질병관련보장특약','선택계약','질병관련','상해관련']:group=non[0]
  else:name=current
  causes=[clean(v) for v in row[ci:ai] if v];cause=' '.join(causes);amount=clean(row[ai])
  if not cause:cause=carrycause
  else:carrycause=cause
  if amount:carryamount=amount
  else:amount=carryamount
  if not name:
   if prev and tab['page']==prev['end_page']+1 and not any(v for v in row[:ci]):
    prev['cause']+=' '+cause;prev['amount']+=' '+amount;prev['end_page']=tab['page']
   continue
  # Skip table notes and section labels.
  if any(v in co(name) for v in ['주)보험','※','상품요약서','지급금액','지급사유','가입시','계약종류']) or len(name)>260:continue
  if not cause or not amount:
   issues.append(dict(doc=di,summary=si,page=tab['page'],name=name,reason='지급표 병합 셀 추가 대조',cause=cause,amount=amount));continue
  # Correct the one explicitly merged premium-waiver amount in summary doc4.
  if '보험료납입면제대상' in co(name) and si==4:amount='특약가입금액(최초 1회한)'
  # Keep the folder's stated underwriting and contract type.
  folder=M[di]['product']
  if '일반심사' in folder and any(v in co(name) for v in ['간편맞춤고지','간편건강고지']):continue
  if '간편맞춤고지' in folder and '간편맞춤고지' not in co(name) and di in [8,65]:continue
  typematch=re.match(r'([1-4]종)\s*\(',cause)
  if typematch:
   foldertypes=re.findall(r'([1-4]종)\(',folder)
   if foldertypes and typematch[1] not in foldertypes:continue
   name+=' / '+typematch[1];cause=re.sub(r'^[1-4]종\s*\([^)]*\)','',cause).strip()
  for alias in aliases(name):
   if not alias:continue
   if '일반심사' in folder and '간편' in alias:continue
   if '간편맞춤고지' in folder and '간편' not in alias and di in [8,65]:continue
   b=dict(doc=di,summary=si,page=tab['page'],end_page=tab['page'],name=alias,group=group,cause=cause,amount=amount,table=tab['table'],row=ri)
   # Explicit subgroup display is kept in name and source trace.
   benefits.append(b);prev=b;lastslot[slot]=b
# Formatting of source operative clauses: omit administrative and discussion paragraphs.
def concise(s):
 s=clean(s);s=re.sub(r'제\s*\d+\s*조(?:의\s*\d+)?\s*\([^()]*(?:\([^()]*\)[^()]*)*\)(?:\s*제\d+항)?','',s)
 s=re.sub(r'\(이하[^)]*\)','',s);s=re.sub(r'^[①-⑳\s]+','',s)
 return s.strip()
def clauses(sec,name,event,rawamount):
 cond=[];defs=[]
 if not sec:return cond,defs
 bc=co(sec['body']);nc=co(name);ev=co(event)
 if '암' in nc and '암보장개시일' in bc and '90일' in bc and '면책없음' not in nc and not any(v in nc for v in ['유사암','갑상선암수술후']):
  cond.append('일반암 보장은 최초계약일(부활일)을 포함하여 90일이 지난 다음 날부터 시작합니다.'+(' 갱신계약은 갱신일부터 보장합니다.' if '갱신형' in nc else ''))
 if '후유장해' in nc:
  cond.append('장해분류표의 지급률로 판정하며 같은 부위의 중복 장해는 높은 지급률을 적용합니다. 기지급 장해가 같은 부위에서 악화되면 기지급분을 차감합니다.')
 if '수술' in nc:
  if '동시에' in bc and '가장높은' in bc:cond.append('동시 수술은 가장 높은 지급액의 한 종류를 지급하며 서로 다른 치료목적의 독립 수술은 약관상 예외를 적용합니다.')
  if '흡인' in bc and '천자' in bc:cond.append('약관상 치료 목적의 수술이어야 하며 흡인·천자·신경차단 등 수술 정의에서 제외하는 행위는 보장하지 않습니다.')
 if '허가치료' in nc and '식품의약품안전처' in bc:
  cond.append('식약처 허가 효능·효과 범위 또는 약관이 인정하는 심평원 승인 요법으로 실제 약물을 투여해야 합니다.')
 for art in sec['articles']:
  at=co(art['title'])
  if not any(v in at for v in ['세부규정','보상하는','지급사유','보장개시','보상한도','공제','자기부담','정의','지급하지','보상하지']):continue
  blocks=re.split(r'[①-⑳]',art['text'])
  for block in blocks:
   q=concise(block);cq=co(q)
   if len(q)<15 or len(q)>1300:continue
   if any(v in cq for v in ['합의하지못','제3자','연명의료','보험계약대출','계약자적립액','청구서','지정대리','증거를제출','변경통지','알려드립니다','금융위원회','「보험료및해약','위험을증가','특약보험료의납입','준용규정','예시안내','보험료납입면제','회사양식']):continue
   if '정의' in at and not any(v in cq for v in ['제외','허가','승인','보상','진단','종합병원','요양병원','등급','간병인','치료']):
    continue
   if '정의' in at:
    # First definitional paragraph; classification lists are retained in the source.
    if len(q)<550 and q.startswith(('이특약','이 특약','이 특별','이특별')):defs.append(q)
    continue
   if not any(v in cq for v in ['최초','한도','연간','감액','50%','차감','공제','제외','면책','90일','180일','365일','보장개시','지급하지','보상하지','재발','재진단','다시입원','평균사용금액','8만원']):continue
   q=re.split(r'【|용어해설|예시안내|\[별표',q)[0].strip()
   if q and len(q)<750:cond.append(q)
 return list(dict.fromkeys(cond)),list(dict.fromkeys(defs))[:1]
for b in benefits:
 di=b['doc'];sec,score=sectionmatch(di,b['name'],b['group'])
 name=b['name'];cause=clean(b['cause']);raw=clean(b['amount']);cond,defs=clauses(sec,name,cause,raw)
 # Limits and reductions printed in the table are authoritative.
 for v in re.findall(r'\([^)]*(?:최초|각각|회한|한도|미만|일이상|이상경과)[^)]*\)',cause+' '+raw):cond.insert(0,v.strip('()')+'.')
 target=re.sub(r'\([^)]*(?:최초|회한|한도)[^)]*\)','',cause).strip()
 target='피보험자: '+target+' '+' '.join(defs)
 amount='보험증권에 정한 해당 담보 가입금액을 기준으로 지급합니다. 지급기준: '+raw+'. 실제 금액은 계약별 가입금액·세부보장 금액에 따라 결정됩니다.'
 if '손해' in name or any(v in co(raw) for v in ['실제부담','실손','보험가입금액한도','보상한도','지출한','손해액']):
  amount='실제 보장대상 손해·비용을 계약의 해당 담보 가입금액 한도 안에서 보상합니다. 지급표 기준: '+raw+'. 자기부담금·손해액 산식은 해당 담보의 계약 조건을 적용합니다.'
 if '후유장해지급률' in co(raw) or '×' in raw:
  amount='계약의 해당 담보 가입금액 × 약관에서 판정한 후유장해지급률. 지급표 기준: '+raw+'.'
 if '보험료납입면제대상' in name:
  amount='납입면제대상 사유 발생 시 해당 특약 가입금액을 지급하는 정액 보장입니다. 보험료 납입면제 제도와 별도 현금 보험금을 구분합니다. 지급표: '+raw+'.'
 if not sec:
  # The basic contract is proven from the summary, source-page keyword and main-contract chapter.
  hits=[j+1 for j,t in enumerate(CP[di]) if canon(name).split('/')[0] in t and '보험가입금액' in t and j>20]
  ps=hits[0] if hits else 1;pe=min(ps+4,M[di]['pages'])
  review='상품요약서 지급표 기준. 같은 제목의 개별 약관 조문은 추가 대조 필요.'
 else:ps,pe=sec['start'],sec['end'];review='상품요약서 지급표와 같은 담보의 약관 조문을 대조.'
 add(di,name,target,amount,' '.join(dict.fromkeys(cond)),ps,pe,b['summary'],f'{b["page"]}–{b["end_page"]}',review,b)
(R/'records_health.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8')
(R/'benefits.json').write_text(json.dumps(benefits,ensure_ascii=False,indent=2),encoding='utf8')
(R/'table_issues.json').write_text(json.dumps(issues,ensure_ascii=False,indent=2),encoding='utf8')
print('HEALTH',len(records),'unlinked',sum('추가 대조' in r['review'] for r in records),'issues',len(issues))
print('COUNTS',collections.Counter(r['doc'] for r in records))
print('UNLINKED',[(r['doc'],r['coverage_name']) for r in records if '추가 대조' in r['review']][:45])


# Insurance type-specific rows whose source tables use a different layout.
def pagehits(di,term,minpage=15):
 return [i+1 for i,t in enumerate(P[di]) if co(term) in co(t) and i+1>=minpage]
def arttext(sec,terms):
 return ' '.join(clean(a['text']) for a in sec['articles'] if any(t in co(a['title']) for t in terms))
def operative(sec,terms):
 pieces=[]
 for a in sec['articles']:
  if not any(t in co(a['title']) for t in terms):continue
  for q in re.split(r'[①-⑳]|(?<=다\.)\s+',a['text']):
   q=concise(q);cq=co(q)
   if 18<len(q)<600 and not any(v in cq for v in ['이하','다음과같','아래의','회사양식','준용','제3자','청구','서류','제출','약관을따','통지','계약을해지','법률개정','손해보험협회','환급금','소유권','대위권','예시','용어','보험료','계약자적립액']):
    if any(v in cq for v in ['지급','보상','한도','만원','원','공제','부담','제외','비용','치료','도난','상해','날','시간']):pieces.append(q)
 return list(dict.fromkeys(pieces))
# Standard indemnity medical insurance: verified native coverage percentages and annual limits.
for di in sorted(medical):
 pp=P[di];tax='상해·질병 급여 및 비급여 실손의료비'
 base='실제 부담한 보장대상 의료비를 보상하며 본인부담상한제 환급대상 금액은 제외합니다. 여러 실손계약이 있으면 비례분담하고 실제 부담액을 초과하여 지급하지 않습니다.'
 si=next((i for i,m in enumerate(M) if m['product']==M[di]['product'] and m['kind']=='상품요약서'),None)
 for risk in ['상해','질병']:
  for kind in ['급여 입원','급여 통원','비급여 입원','비급여 통원','상급병실료 차액']:
   hits=pagehits(di,'80%' if kind.startswith('급여') else '70%' if kind.startswith('비급여') else '상급병실료차액')
   ps=min(hits) if hits else 1;pe=min(max(hits) if hits else M[di]['pages'],110)
   target=f'피보험자가 {risk}로 국내 의료기관에서 치료받고 실제 부담한 '+('건강보험·의료급여의 급여 본인부담 의료비.' if kind.startswith('급여') else '비급여 의료비. 도수치료·체외충격파·증식치료, 비급여 주사 및 비급여 MRI/MRA는 별도 3대 비급여 담보로 구분합니다.' if kind.startswith('비급여') else '입원 시 기준병실과 상급병실의 비급여 병실료 차액.')
   if kind=='급여 입원':amt='보장대상 급여 본인부담금의 80%. 해당 상해급여·질병급여의 입원·통원 합산 연간 한도는 계약 가입금액(최대 5,000만원)입니다.';condition='본인부담률 20%.'
   elif kind=='급여 통원':amt='외래·처방조제 합산 보장대상 급여 본인부담금에서 공제금액을 차감. 공제금액은 병·의원 1만원 또는 종합·상급종합병원 2만원과 의료비의 20% 중 큰 금액. 통원 1회당 계약 가입금액(최대 20만원), 입원·통원 합산 연간 최대 5,000만원.';condition='통원 1회에는 외래와 처방조제를 합산합니다.'
   elif kind=='비급여 입원':amt='보장대상 비급여 의료비의 70%. 상해·질병별 입원·통원 합산 연간 계약 가입금액 한도(최대 5,000만원).';condition='자기부담률 30%. 3대 비급여와 상급병실료 차액은 해당 별도 지급기준을 적용합니다.'
   elif kind=='비급여 통원':amt='외래·처방조제 합산 비급여 의료비에서 3만원과 의료비의 30% 중 큰 금액을 차감. 통원 1회당 계약 가입금액(최대 20만원), 상해·질병별 연간 100회, 입원·통원 합산 연간 최대 5,000만원.';condition='통원 1회에는 외래와 처방조제를 합산합니다.'
   else:amt='비급여 상급병실료 차액의 50%, 1일 평균 10만원 한도. 상해·질병 비급여의 입원·통원 합산 연간 가입금액 한도 내 지급.';condition='1일 평균 금액은 총 상급병실료 차액을 총 입원일수로 나누어 계산합니다.'
   add(di,risk+' '+kind+' 실손의료비',target,amt,condition+' '+base,ps,max(ps,pe),si,'전체')
 for name,limit,count in [('도수치료·체외충격파치료·증식치료','350만원','50회'),('비급여 주사료','250만원','50회'),('비급여 MRI·MRA','300만원','횟수 제한 없이 금액 한도')]:
  hits=pagehits(di,'350만원' if '도수' in name else '250만원' if '주사' in name else '300만원');ps=min(hits) if hits else 1;pe=max(hits) if hits else M[di]['pages']
  extra=' 최초 10회 보장 후 객관적 검사결과로 증상 개선·병변 호전 등이 확인되어야 10회 단위로 연간 한도까지 추가 보장합니다.' if '도수' in name else ' 영양제·비타민 주사는 약제별 식약처 허가·신고사항의 치료목적에 맞게 사용한 경우에 한합니다.' if '주사' in name else ' 조영제·판독료를 포함하고 검사 부위 수와 무관하게 1회 검사 비용으로 계산합니다.'
  add(di,'3대 비급여 / '+name,'피보험자의 상해·질병 치료 목적으로 실제 부담한 '+name+' 비급여 비용.','1회 치료·검사 의료비에서 3만원과 의료비의 30% 중 큰 금액을 공제. 계약일부터 매 1년간 '+limit+' 및 '+count+' 한도.',extra.strip()+' '+base,ps,pe,si,'전체')
# Automobile base coverage for actual policy documents.
for di in sorted(motor):
 si=next((i for i,m in enumerate(M) if m['product']==M[di]['product'] and m['kind']=='상품요약서'),None)
 vehicle='보험증권에 기재한 이륜자동차' if '이륜' in M[di]['product'] else '보험증권에 기재한 피보험자동차'
 specs=[
 ('대인배상Ⅰ / 사망',f'{vehicle}의 소유·사용·관리 중 사고로 타인이 사망하여 피보험자가 법률상 손해배상책임을 부담한 경우.','피해자 1인당 실제 법률상 손해배상액을 책임보험 지급기준에 따라 보상하며 사망 한도 1억5,000만원.','사망보험금 지급기준과 법정 최저 지급액을 적용합니다.'),
 ('대인배상Ⅰ / 부상',f'{vehicle} 사고로 타인이 다쳐 피보험자가 법률상 손해배상책임을 부담한 경우.','피해자 1인당 상해급별 책임보험 한도 내 실제 손해액. 최고 한도 3,000만원.','상해급별 한도를 적용합니다.'),
 ('대인배상Ⅰ / 후유장애',f'{vehicle} 사고로 타인에게 후유장애가 남아 피보험자가 법률상 손해배상책임을 부담한 경우.','피해자 1인당 후유장애 급별 책임보험 한도 내 손해액. 최고 한도 1억5,000만원.','후유장애 급별 한도를 적용합니다.'),
 ('대인배상Ⅱ',f'{vehicle} 사고로 다른 사람의 사망·부상에 대한 법률상 손해배상책임을 부담한 경우.','대인배상Ⅰ 지급액을 초과하는 법률상 손해배상액과 약관상 인정 비용을 해당 계약 가입금액 한도에서 보상합니다. 가입한도가 무한인 계약은 피해자 1인당 무한 한도를 적용합니다.','기지급 대인배상Ⅰ과 중복 지급하지 않습니다.'),
 ('대물배상',f'{vehicle} 사고로 다른 사람의 재물을 멸실·훼손하여 법률상 손해배상책임을 부담한 경우.','1사고당 실제 법률상 손해배상액과 약관상 비용을 계약 가입금액 한도에서 지급. 법정 의무가입 부분은 2,000만원이며 그 초과한도는 계약에서 정합니다.','피보험자의 소유·사용·관리 재물 등 약관상 면책 재물은 제외합니다.'),
 ('자기신체사고',f'{vehicle}의 사고로 자기신체사고 담보의 피보험자가 사망·부상하거나 후유장애가 발생한 경우.','사망·후유장애는 계약 가입금액과 장해급별 지급기준, 부상은 실제 치료비를 부상급별 한도 내에서 지급합니다. 실제 한도는 보험증권의 사망·부상·후유장애 가입금액으로 결정됩니다.','다른 배상의무자에게 받은 금액 등 약관상 공제액을 차감합니다.'),
 ('무보험자동차에 의한 상해',f'무보험자동차·뺑소니자동차의 사고로 해당 담보의 피보험자가 사망·부상한 경우. {vehicle}의 지정 피보험자 범위를 적용합니다.','약관 보험금 지급기준에 따른 손해액과 비용에서 공제액을 빼고 피해자 1인당 계약 가입금액 한도로 보상합니다.','배상의무자가 존재해야 하며 대인배상Ⅰ·정부 보장사업·배상의무자에게 받은 금액 등은 공제합니다.'),
 ('자기차량손해',f'{vehicle}이 다른 자동차와 충돌·접촉하거나 전체가 도난되어 입은 직접 손해.','사고 당시 차량 보험가액 및 계약 가입금액 한도 내 수리·복구비 또는 전손 손해액에서 보험증권의 자기부담금을 차감합니다.','일부 부품·부속품만의 도난은 제외합니다. 단독사고·침수 등은 보장확대 특약의 별도 범위를 확인합니다.')
 ]
 for name,target,amount,cond in specs:
  term=name.split(' / ')[0];hits=[i+1 for i,t in enumerate(P[di][:60]) if co(term) in co(t) and any(v in co(t) for v in ['보상하는','보상한도','보험금의종류','지급보험금','보험금은'])]
  ps=min(hits) if hits else 3;pe=max(hits) if hits else min(60,M[di]['pages'])
  add(di,name,target,amount,cond,ps,pe,si,'전체',review='보통약관의 해당 보장종목·지급기준·자동차보험 상품요약서 대조.')
 # Only payable extensions; discount, driver restriction and payment administration are not independent coverage.
 whitelist=['자동차상해','상해간병','상급병실','자녀(만18세','음주·무면허','자기차량손해보장확대','렌트비용','차량운반','신차손해','전손시대체','렌터카운전','교통약자','법률비용','다른자동차운전','보험대차','전기자동차배터리','전기자동차충전','하이카서비스','반려동물사고','임직원사고','임직원치료','주차위반피견인','기계장치에관한','대물배상가입금액확장','자율주행차위험','품질인증부품사용','리스자동차인도']
 seen=set()
 for sec in S.get(str(di),[]):
  name=co(sec['name']).split('다.')[-1];name=re.sub(r'^\d+\.?','',name)
  if not any(v in name for v in whitelist) or len(sec['body'])<160 or name in seen:continue
  seen.add(name);targetpart=arttext(sec,['보상하는손해','보상내용','피보험자']);pay=operative(sec,['보상하는손해','보상내용','보험금','보상한도']);excl=operative(sec,['보상하지','보상하지않는','지급보험금','보상한도'])
  if not targetpart:targetpart=clean(sec['body'][:850])
  target=targetpart.split('회사가 이 특별약관에서 지급하는')[0]
  target=concise(target);target=re.split(r'용어정의|용어해설',target)[0]
  if len(target)>650:target=target[:target.rfind('다.',0,650)+2] or target[:650]
  amount=' '.join(q for q in pay if any(v in co(q) for v in ['원','한도','지급','차감']))[:1800]
  if not amount:amount='보장대상 손해·비용을 해당 계약 가입금액과 연결 담보의 지급기준에 따라 보상합니다. 구체적 금액은 보험증권의 선택 가입금액과 해당 사고 손해액으로 결정됩니다.'
  cond=' '.join(excl)[:1300]
  if '법률비용지원' in name:
   target='피보험자동차 사고로 피보험자가 형사책임을 부담하며 약관상 대상 사고에 대해 벌금·변호사선임비용·형사합의금을 실제 부담한 경우.'
  add(di,name,target,amount,cond,sec['start'],sec['end'],si,'전체',review='자동차 특별약관의 보상손해·피보험자 범위·비용·한도 대조.')
# Travel policies: every operative payable rider, plus the main accident and overseas/domestic medical split.
for di in sorted(travel):
 si=next((i for i,m in enumerate(M) if m['product']==M[di]['product'] and m['kind']=='상품요약서'),None)
 period='보험증권에 정한 해외여행·체류기간 중'
 for name,target,amt in [
 ('상해사망',period+' 급격하고 우연한 외래 사고의 직접 결과로 사고일부터 1년 이내 사망한 피보험자.','계약의 상해사망 가입금액 전액.'),
 ('상해후유장해',period+' 발생한 상해의 직접 결과로 장해분류표의 3~100% 지급률에 해당하는 후유장해가 남은 피보험자.','상해후유장해 가입금액 × 장해분류표의 해당 지급률.'),
 ('해외발생 상해의료비',period+' 발생한 상해로 해외 의료기관에서 치료받고 실제 부담한 의료비.','국외 의료기관의 실제 보장대상 의료비를 계약의 해당 담보 가입금액 한도 내 지급. 자기부담 여부·액수는 보험증권의 약정에 따라 적용합니다.'),
 ('해외발생 질병의료비',period+' 발생한 질병으로 해외 의료기관에서 치료받고 실제 부담한 의료비.','국외 의료기관의 실제 보장대상 의료비를 계약의 해당 담보 가입금액 한도 내 지급. 자기부담 여부·액수는 보험증권의 약정에 따라 적용합니다.')]:
  term='보험금의지급사유' if name.startswith('상해') else '해외'
  hits=[i+1 for i,t in enumerate(P[di]) if term in co(t) and ('1년' in co(t) if name.startswith('상해') else '의료비' in co(t))]
  ps=min(hits) if hits else 1;pe=min(max(hits) if hits else len(P[di]),80)
  add(di,name,target,amt,'여행·체류기간과 사고·발병 및 치료의 관계가 약관상 보장범위를 충족해야 합니다. 실제 비용형 보장은 중복 실손계약이 있으면 비례분담합니다.',ps,max(ps,pe),si,'전체',review='보통약관 상해 지급사유 및 해외의료비 담보 대조.')
 # Domestic medical is the native standard 4th-generation indemnity basis, separate from overseas costs.
 for risk in ['상해','질병']:
  for typ,amt,con in [
   ('국내 급여 입원','실제 보장대상 급여 본인부담금의 80%. 국내 해당 담보의 입원·통원 합산 연간 계약 가입금액 한도(최대 5,000만원).','자기부담률 20%.'),
   ('국내 급여 통원','급여 본인부담 의료비에서 병·의원 1만원 또는 종합·상급종합병원 2만원과 의료비의 20% 중 큰 금액을 공제. 통원 1회당 계약 가입금액(최대 20만원) 및 연간 가입금액 한도.','외래·처방조제 합산.'),
   ('국내 비급여 입원','보장대상 비급여 의료비의 70%. 입원·통원 합산 연간 계약 가입금액 한도(최대 5,000만원).','3대 비급여와 상급병실료 차액은 별도 지급기준.'),
   ('국내 비급여 통원','비급여 의료비에서 3만원과 의료비의 30% 중 큰 금액을 공제. 통원 1회당 계약 가입금액(최대 20만원), 연간 100회 및 가입금액 한도.','외래·처방조제 합산.')]:
   hits=pagehits(di,'80%' if '급여' in typ and '비급여' not in typ else '70%')
   ps=min(hits) if hits else 1;pe=max(hits) if hits else min(80,M[di]['pages'])
   add(di,risk+' '+typ+' 실손의료비',period+f' 발생한 {risk}로 국내 의료기관에서 치료받아 실제 부담한 '+typ+' 의료비.',amt,con+' 본인부담상한제 환급대상은 제외하고 여러 실손계약은 비례분담합니다.',ps,pe,si,'전체',review='해외여행·체류 급여 및 비급여 실손 특별약관 지급표·한도 대조.')
 for sec in S[str(di)]:
  name=canon(sec['name'])
  if any(v in name for v in ['비급여실손','비가입자','보험금만의지급','보장제외','공동인수','대리청구','보험전환','환율','전자서명','계약','스포츠','동반인','부부보장','가족보장','단체취급','전쟁위험']):continue
  targettext=arttext(sec,['보상하는손해','지급사유','보험목적의범위'])
  if not targettext:continue
  pp=operative(sec,['보상하는손해','지급사유','지급보험금의계산','지급보험금','보상한도'])
  cost=' '.join(v for v in pp if any(k in co(v) for k in ['금액','만원','한도','보험가입금액','비용','보험금']))[:1500]
  condition=' '.join(operative(sec,['보상하지않는','지급에관한세부','보상한도']))[:1100]
  target=concise(targettext);target=re.split(r'\[용어|용어해설|②',target)[0]
  if len(target)>700:target=target[:target.rfind('다.',0,700)+2] or target[:700]
  if not cost:cost='실제 보장대상 손해·비용 또는 약정 보험금을 해당 담보 가입금액 한도 내 지급합니다. 구체적 금액은 보험증권의 가입금액과 실제 손해액으로 결정됩니다.'
  if '항공기납치' in name:cost='납치 상태 1일당 7만원, 20일 한도.' 
  add(di,name,target,cost,condition,sec['start'],sec['end'],si,'전체',review='해외여행·체류 개별 특별약관의 지급사유·비용 산식·기간 대조.')
# Savings maturity benefit is separate from accidental-death coverage.
for di in [2,14]:
 hits=pagehits(di,'만기환급금의지급')
 si=di-1
 add(di,'적립부분 / 만기환급금','보험기간이 끝날 때까지 유지된 저축보험의 보험수익자.','적립순보험료를 보험료·해약환급금 산출방법서에 따라 연단위 복리로 계산한 만기환급금. 가입 후 3년 이내 연 3.1%, 이후 저축성 공시이율Ⅴ를 적용합니다. 최저보증은 5년 이하 1.25%, 5년 초과 10년 이하 1.0%, 10년 초과 0.3%.','일시납의 계약체결비용 원금·이자, 자동대출납입 보험료·이자 및 보험계약대출 원리금은 차감합니다. 중도인출은 적립액과 최종 만기환급금을 감소시킵니다.',min(hits) if hits else 1,max(hits) if hits else M[di]['pages'],si,'2–4',review='보통약관 만기환급금과 상품요약서 적립이율·공제액 대조.')
# Remove exact duplicate table passages only, keeping materially different cause/amount variants.
unique=[];seen=set()
for r in records:
 key=tuple(r[k] for k in ['product_name','coverage_name','coverage_target','coverage_amount'])
 if key in seen:continue
 seen.add(key);unique.append(r)
records=unique
for i,r in enumerate(records,1):
 r['id']=i
 assert all(r[k] for k in ['company_name','product_name','coverage_name','coverage_target','coverage_amount']),r['coverage_name']
 assert '해당 특약을 가입한 계약에 적용합니다' not in r['coverage_conditions']
(R/'records.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8')
print('TOTAL',len(records),'PRODUCTS',len(set(r['product_name'] for r in records)));print('COUNTS',collections.Counter(r['doc'] for r in records))




