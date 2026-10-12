from pathlib import Path
import json,re,unicodedata,statistics
from datetime import datetime,timezone,timedelta
R=Path('work/heungkuk');M=json.loads((R/'manifest.json').read_text(encoding='utf8'));S=json.loads((R/'sections.json').read_text(encoding='utf8'));rr=json.loads((R/'records_base.json').read_text(encoding='utf8'));P={int(k):json.loads((R/f'doc{k}.json').read_text(encoding='utf8')) for k in S}
def co(s):return re.sub(r'\s+','',s or '')
def norm(s):
 s=unicodedata.normalize('NFKC',co(s)).replace('·','ㆍ').replace('보험료납입면제대상보장','보험료납입면제대상')
 s=re.sub(r'\((?:간편가입|통합간편가입형|건강고지형|갱신형[^)]*)\)','',s).replace('질병질병','질병')
 return s
lookup={int(k):{norm(v):s for s in a for v in s['aliases']} for k,a in S.items()}
stamp=datetime.now(timezone(timedelta(hours=9))).isoformat(sep=' ',timespec='seconds');rows=[];pending=[]
# restore headings split across consecutive pages even if the repeated amount was populated
i=0
while i<len(rr):
 x=rr[i];di=int(Path(x['source_file']).parent.name=='' or next(m['key'][3:] for m in M if m['path']==x['source_file']));n=x['coverage_name'];n=n.replace('80%이상))','80%이상)')
 if i+1<len(rr) and rr[i+1]['source_file']==x['source_file']:
  nxt=rr[i+1];joined=n+nxt['coverage_name']
  if norm(joined) in lookup[di] and norm(n) not in lookup[di]:
   n=joined;x['raw']['cause']+=' '+nxt['raw']['cause'];x['raw']['amount']+=' '+nxt['raw']['amount'];x['summary_page']=str(x['raw']['page'])+'–'+str(nxt['raw']['page']);i+=1
 if '*「잔고」' in n:n=n.split('*「잔고」')[0]
 n=n.replace('질병질병','질병');x['coverage_name']=n
 sec=lookup[di].get(norm(n));proof='제목 정확 대조'
 if not sec:
  # basic contract is outside selected rider sections
  if '일반상해후유장해(80%이상)' in n and di in [25,28] or n.startswith('암후유장해(80%이상)') and di in [43,46]:
   first=min(s['start'] for s in S[str(di)]);sec={'name':'보통약관','start':max(1,first-40),'end':first-1,'articles':[]};proof='보통약관 기본담보 지급표 대조'
  else:
   # exact distinct medical name in the body can identify a text-source page
   hits=[j+1 for j,t in enumerate(P[di]) if norm(n) in norm(t)]
   hits=[v for v in hits if 60<=v<len(P[di])-20]
   if hits:
    page=hits[0];sec=next((s for s in S[str(di)] if s['start']<=page<=s['end']),None);proof='본문 담보명·지급표 대조'
 if sec:x['source_page']=f'{sec["start"]}–{sec["end"]}';x['review']=proof+'. 상품요약서 지급표의 담보별 금액·단위를 유지.'
 else:x['review']='상품요약서 지급표 기준. 약관 제목 일치 항목을 추가 확인해야 함.';x['source_page']='';pending.append(dict(product=x['product_name'],name=n,summary=x['summary_page']))
 cause=x['raw']['cause'];amount=x['raw']['amount'];cc=co(cause);ac=co(amount);body=' '.join(a['text'] for a in sec['articles']) if sec else '';bc=co(body)
 c=[]
 for v in re.findall(r'\([^)]*(?:최초|각각|회한|한도|미만|이상|진단후)[^)]*\)',cause):c.append(re.sub(r'\s+',' ',v).strip('()')+'.')
 if '암' in n and '면책없음' not in n and '암보장개시일' in bc and '90일' in bc:c.append('일반암 보장은 최초계약일(부활일)을 포함하여 90일이 지난 다음 날부터 시작하며 갱신계약은 갱신일부터 보장합니다. 유사암은 해당 보장의 별도 보장개시 기준을 적용합니다.')
 if '면책없음' in n:c.append('암 90일 면책기간을 적용하지 않는 지급형입니다.')
 if '감액없음' in n:c.append('계약 초기 감액을 적용하지 않는 지급형입니다.')
 if '재진단' in n or '재발암' in n:
  extra=re.split(r'주\)|주\d?\)',cause)[-1]
  if extra!=cause:c.append(re.sub(r'\s+',' ',extra).replace('※ 자세한 사항은 약관 참조','').strip())
 if '후유장해' in n:
  c.append('장해분류표의 지급률로 판정합니다. 같은 부위의 중복 장해는 높은 지급률을 적용하고, 기지급 장해가 같은 부위에서 악화되면 기지급분을 차감합니다.')
  if '180일' in bc:c.append('180일 내 장해가 확정되지 않으면 180일째 의사 진단에 따른 고정 상태를 기준으로 하되 별도 판정시기가 있는 장해는 그 기준을 따릅니다.')
 if '입원비' in n:
  if '동일한' in bc and ('합산' in bc or '더합니다' in bc):c.append('같은 상해·질병으로 재입원하거나 병원을 옮긴 경우 계속입원으로 보아 입원일수를 합산합니다.')
  if '보험기간이끝났' in bc:c.append('보장개시 후 시작한 계속입원은 보험기간 종료 후에도 퇴원 전까지 해당 일수 한도 내에서 지급합니다.')
 if '수술비' in n and '수술' in bc:
  if '동시에' in bc and '가장높은' in bc:c.append('동시 수술은 가장 높은 지급액의 수술 한 종류를 지급하며 서로 다른 신체부위·치료목적의 독립 수술은 약관상 예외를 적용합니다.')
  if '흡인' in bc and '천자' in bc:c.append('치료 목적의 약관상 수술이어야 하며 흡인·천자·신경차단과 미용·피임·검사만을 위한 조치는 수술보장에서 제외됩니다.')
  if '365일' in bc:c.append('동일 질병 수술의 재지급은 약관상 365일 경과 기준을 충족해야 합니다.')
 if '허가치료' in n and '식품의약품안전처' in bc:
  c.append('식약처 허가 효능·효과 내 사용 또는 약관에서 인정한 심평원 승인요법이어야 하며, 처방만으로는 지급하지 않고 실제 약물 투여가 필요합니다.')
 if '도수' in n and '횟수' in bc:c.append('약관에서 정한 치료행위와 치료 횟수·연간 한도를 적용합니다.')
 if '주요치료' in n and '진단후10년' in n:c.append('최초 진단일부터 10년의 지급기간 안에서 실제 주요치료를 받은 때 지급합니다. 다른 대상 질환을 나중에 진단받아도 최초 진단 기준의 지급기간을 새로 시작하지 않습니다.')
 if '납입면제대상' in n:c.append('지정된 진단·치료·장해사유 중 최초 1회 발생 시 담보 가입금액을 지급하며 같은 담보의 여러 사유를 중복 지급하지 않습니다.')
 # unique high-value source sentences: deductions, recurrence, annual period, additional therapy constraints
 if sec:
  for a in sec['articles']:
   if not any(v in a['title'] for v in ['세부규정','보장개시','보상하지','지급하지']):continue
   for sent in re.split(r'(?<=다\.)\s+',re.sub(r'\s+',' ',a['text'])):
    ss=co(sent)
    if not any(v in ss for v in ['차감','공제','한도','최초계약','재발','전이','이미지급','연간이라','보험금지급기간이라']):continue
    if any(v in ss for v in ['제3자','합의','계약자적립액','준용','특별약관의소멸','법률','예시','장해분류표','회사는피보험자','다음각호','아래의','보험금을지급할때','연단위복리']):continue
    if 30<len(sent)<500 and sent.strip().endswith('다.'):
     sent=re.sub(r'제\s*\d+조(?:의\d+)?\s*\([^()]*(?:\([^()]*\)[^()]*)*\)(?:\s*제\d+항)?','',sent);sent=re.sub(r'제\d+항(?:에따라|의경우)?','',sent);sent=re.sub(r'^[①-⑳\s]+','',sent).strip()
     if not sent.startswith(('에서','의','에따라','「')):c.append(sent)
 c=list(dict.fromkeys(c));x['coverage_conditions']=' '.join(c) if c else '보험기간 중 위 지급사유가 발생해야 합니다. 해당 보장의 진단·치료·사고 범위에 따라 지급합니다.'
 x['created_at']=stamp;x['updated_at']=stamp;rows.append(x);i+=1
# add six standard medical product variants, splitting inpatient/outpatient/room differences
def add(di,name,target,amount,cond,ps,pe,si):
 prod=re.sub(r'^판매완료__\d+_','',M[di]['product']).replace('_',' ')
 rows.append(dict(id=0,company_name='흥국화재',product_name=prod,coverage_name=name,coverage_target=target,coverage_amount=amount,coverage_conditions=cond,created_at=stamp,updated_at=stamp,source_file=M[di]['path'],source_page=f'{ps}–{pe}',summary_file=M[si]['path'],summary_page='3–5' if di!=20 else '3–4',review='실손 지급표·공제금액·가입금액별 통원 한도 대조.',raw=None))
for di in [2,5,8,11,14,17]:
 p=json.loads((R/f'doc{di}.json').read_text(encoding='utf8'))
 relevant=[i+1 for i,t in enumerate(p) if '80%' in t and ('보상' in t or '보장' in t)];ps=min(v for v in relevant if v>20);pe=max(v for v in relevant if v<85)
 base='실제 부담한 국내 보장대상 의료비만 보상하며 본인부담상한제 환급대상 금액은 제외합니다. 다른 실손보험과 중복 시 비례분담하고 실제 부담액을 초과해 지급하지 않습니다. 미용·예방·건강검진만을 위한 비용 및 약관상 제외 치료는 보상하지 않습니다.'
 for risk in ['상해','질병']:
  for kind in ['입원','통원']:
   name=risk+'급여의료비 / '+kind
   target=f'피보험자가 {risk}의 치료를 위해 의료기관에 {kind}하여 실제 부담한 건강보험·의료급여 급여 본인부담금.'+(' 외래와 처방조제비를 합산합니다.' if kind=='통원' else '')
   amount='급여 보장대상 본인부담금의 80%. 입원·통원 합산 연간 해당 가입금액 한도(1천만·3천만·5천만원 중 계약에서 정한 금액).' if kind=='입원' else '1회 급여 외래·처방조제비에서 의료기관별 정액 공제(일반 1만원, 종합·상급종합 등 2만원)와 보장대상 금액의 20% 중 큰 금액을 차감. 가입금액 1천만/3천만/5천만원일 때 통원 1회 한도는 각각 10만/15만/20만원.'
   add(di,name,target,amount,base,ps,pe,di-1)
  for kind in ['입원','통원','상급병실료차액']:
   target=f'피보험자의 {risk} 치료에 실제 부담한 비급여 의료비. 도수·체외충격파·증식치료, 비급여 주사, MRI/MRA는 3대 비급여 보장에서 구분합니다.'
   amount='비급여 보장대상 입원의료비(병실료 제외)의 70%. 입원·통원 합산 연간 해당 가입금액 한도.' if kind=='입원' else '통원 1회 외래·처방조제비에서 3만원과 보장대상 금액의 30% 중 큰 금액을 차감. 가입금액 1천만/3천만/5천만원일 때 1회 한도 각각 10만/15만/20만원, 연간 100회 한도.' if kind=='통원' else '실제 비급여 병실료의 50%. 입원기간 전체 병실료를 총 입원일수로 나눈 1일 평균금액 기준 10만원 한도.'
   add(di,risk+'비급여의료비 / '+kind,target,amount,base+' 3대 비급여 금액을 일반 비급여 의료비와 중복 보상하지 않습니다.',55, min(80,len(p)),di-1)
 for name,limit,cond in [('도수·체외충격파·증식치료','연간 합산 350만원, 50회','첫 10회 보장 후 객관적 검사로 증상 개선·병변 호전이 확인되어야 10회 단위로 추가 보장합니다.'),('비급여주사료','연간 250만원, 50회','약관상 허가·신고된 약제의 효능·효과와 용법·용량에 따른 치료에 한하며 인정되는 항암·항생·희귀의약품 예외는 별도 비급여 보장 범위를 따릅니다.'),('비급여MRI/MRA','연간 300만원','조영제·판독료를 포함하며 검사별 보장대상 비급여 금액을 합산합니다.')]:
  add(di,'3대비급여의료비 / '+name,'피보험자의 상해·질병 치료에 실제 부담한 '+name+' 관련 비급여 의료비.','1회 보장대상 의료비에서 3만원과 해당 금액의 30% 중 큰 금액을 차감. '+limit+' 한도.','상해·질병 치료행위를 합산해 매년 계약해당일부터 1년 단위 한도를 적용합니다. '+cond+' 중복 실손 가입 시 비례분담합니다.',60,min(80,len(p)),di-1)
di=20
for risk in ['상해','질병']:
 for kind in ['입원','통원','상급병실료차액']:
  amount='보장대상 급여 본인부담금+비급여(병실료 제외)에서 10만원과 금액의 30% 중 큰 금액 차감. 하나의 '+risk+'당 5천만원 한도. 공제금액의 연간 합계가 200만원을 초과하면 초과분 보상.' if kind=='입원' else '방문 1회 급여 본인부담금+비급여에서 2만원과 금액의 30% 중 큰 금액 차감. 1회 20만원, 연간 180회 한도.' if kind=='통원' else '실제 비급여 병실료의 50%. 입원기간 전체 병실료를 입원일수로 나눈 1일 평균금액 10만원 한도.'
  add(di,'유병력자 '+risk+'의료비 / '+kind,'피보험자의 '+risk+' 치료로 실제 부담한 '+kind+' 의료비. 입원·통원 보장대상 급여와 비급여를 합산합니다.',amount,'통원은 외래진료를 대상으로 하며 처방조제비는 제외됩니다. 도수·체외충격파·증식치료, 비급여 주사 및 MRI/MRA는 제외합니다. 다른 실손과 중복 가입 시 비례분담합니다. 건강보험·의료급여를 적용받지 못하면 약관상 공제 후 금액의 40%를 해당 한도 안에서 보상합니다.',32,60,19)
# keep exact duplicate cells once; distinct payout structures remain separately identified
unique=[];seen=set()
for x in rows:
 k=(x['product_name'],x['coverage_name'],x['coverage_target'],x['coverage_amount'])
 if k in seen:continue
 seen.add(k);unique.append(x)
for i,x in enumerate(unique,1):x['id']=i
(R/'records.json').write_text(json.dumps(unique,ensure_ascii=False,indent=2),encoding='utf8');(R/'pending.json').write_text(json.dumps(pending,ensure_ascii=False,indent=2),encoding='utf8')
from collections import Counter
print('FINAL',len(unique),'PENDING',len(pending),'MEDIAN COND',statistics.median(len(x['coverage_conditions']) for x in unique));print(dict(Counter(x['product_name'] for x in unique)))

