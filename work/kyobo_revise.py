import json,re,shutil,statistics
from pathlib import Path
from datetime import datetime,timezone,timedelta
p=Path('work/kyobo/revision');p.mkdir(exist_ok=True)
if not (p/'original.xlsx').exists():shutil.copy2('C:/Users/FAS/Desktop/데이터분석/교보생명_2507_담보분석.xlsx',p/'original.xlsx')
r=json.loads(Path('work/kyobo/records.json').read_text(encoding='utf8'));S=json.loads(Path('work/kyobo/sections.json').read_text(encoding='utf8'));M=json.loads(Path('work/kyobo/manifest.json').read_text(encoding='utf8'))
def co(s):return re.sub(r'\s+','',s)
terms=['보험가입금액','보험계약일','계약자적립액','장해지급률','장해분류표','보장개시일','보험기간','진단확정','피보험자','최초','보험료','납입면제','차회','계약해당일','직접적인','요양병원','연금지급','기타피부암','갑상선암','제자리암','경계성종양','한시장해','입원일수','감액','지급']
def clean(s):
 s=re.sub(r'\s+',' ',s).strip()
 for w in terms:s=re.sub(r'\s*'.join(map(re.escape,w)),w,s)
 s=re.sub(r'\b\d+\s*교보[^①②③④⑤]{0,80}?약관',' ',s)
 return re.sub(r'\s+',' ',s).strip(' .;')
def short(s):
 s=clean(s);s=re.sub(r'제\s*\d+조(?:의\d+)?\s*\([^()]*(?:\([^()]*\)[^()]*)*\)(?:\s*제\d+항)?','',s)
 s=re.split(r'【(?:예시|관련|설명)|<[^>]*예시[^>]*>|\[(?:예시|관련)',s)[0]
 return re.sub(r'\s+',' ',s).strip(' .;')
now=datetime.now(timezone(timedelta(hours=9))).isoformat(sep=' ',timespec='seconds');out=[]
for x in r:
 n=x['coverage_name'];leaf=n.split(' / ')[-1];raw=x['coverage_conditions'];cause=clean(raw.split('\n')[0]);waiver='보험료납입면제' in leaf;annual='연금' in leaf
 key=next(a['key'] for a in M if a['path']==x['source_file']);start=int(re.split('[–-]',x['article_pages'])[0]);s=next((z for z in S[key] if z['start']==start),None)
 target='해당 주계약·특약의 피보험자에 대해 '+cause+'에 해당하는 경우를 보장합니다.'
 target=target.replace('때에 해당하는 경우','경우').replace('경우에 해당하는 경우','경우')
 if '양육연금' in leaf:target='주계약 피보험자의 가족관계등록부상 또는 주민등록상 가입자녀에게 지급하는 사망보험금 분할 연금입니다.'
 if '배우자연금' in leaf:target='부부형의 배우자 피보험자가 약관상 지급 요건을 충족한 경우의 배우자연금입니다. '+cause
 amount=clean(x['coverage_amount'])
 amount=('현금 지급 대신 보험료 납입을 면제하는 보장입니다. ' if waiver else '계약별 적립액·가입금액과 약정 연금형태에 따라 계산하는 지급액입니다. ' if annual else '지급표의 기준가입금액 또는 실제 계약가입금액에 따른 지급기준입니다. ')+amount
 cond=['해당 특약은 실제 가입한 계약에 적용합니다.' if x['type']=='특약' else '보험기간 중 해당 주계약의 지급 요건을 충족해야 합니다.']
 if '전환' in n:cond.append('해당 전환계약의 신청·승낙 및 전환 후 보장조건을 충족해야 합니다.')
 for limit in re.findall(r'\([^)]*(?:최초|한도|1회|\d+일|\d+회|감액)[^)]*\)',cause+' '+x['coverage_amount']):
  q=short(limit).strip('()')
  if q and co(q) not in {co(a.rstrip('.')) for a in cond}:cond.append(q+'.')
 if s:
  texts=[a['text'] for a in s['articles'] if any(k in a['title'] for k in ['세부규정','지급하지','보장개시'])]
  # Numbered payment-table notes often contain the benefit-specific limits.
  texts.extend(z for z in raw.split('\n')[1:] if z.startswith(('(주)','주)')))
  for text in texts:
   text=re.split(r'\(\s*별표\s*\d+|제\s*[3-7]관\s|분류항목\s*분류코드|대상이\s*되는\s*악성신생물',text)[0]
   for block in re.split(r'[①-⑳㉑-㉟]|\(주\)\s*\d+\.|\b주\)\s*\d+\.',text):
    t=co(block)
    if len(t)<15 or any(a in t for a in ['합의하지못','제3자','연명의료중단','의료기관은다음','다음과같이구분','계약자가회사에알려']):continue
    if not waiver and ('납입면제' in t or re.search(r'보험료.{0,20}납입.{0,15}면제',t)):continue
    if not waiver and '장해지급률' in t and '장해' not in co(leaf+cause):continue
    if '장기요양연금' in t and '장기요양' not in leaf and leaf=='생존연금':continue
    if not annual and '사망' not in leaf and '계약자적립액' in t and '사망' in t:continue
    if '암' not in co(leaf+cause) and '암보장개시' in t and '90일' in t:continue
    if not any(a in t for a in ['보장개시','최초','한도','감액','차감','공제','제외','지급하지','중복','180일','365일','90일','30일','보증','갱신','동일한']):continue
    q=short(block)
    if not waiver and '보험료' in t and '해지' in t:
     q=' '.join(z for z in re.split(r'(?<=다\.)\s+',q) if '보장개시' in co(z) and '해지' not in co(z))
    if len(q)>750:
     sentences=re.split(r'(?<=다\.)\s+',q)
     q=' '.join(z for z in sentences if any(a in co(z) for a in ['보장개시','최초','한도','감액','차감','제외','지급하지','중복','180일','365일','90일','30일','보증','갱신','동일한']) and not any(a in co(z) for a in ['예시','제3자','의료기관이란','사망일을확인하는']))
    if q and co(q) not in {co(a.rstrip('.')) for a in cond}:cond.append(q.rstrip('.')+'.')
 if waiver:
  kind=re.search(r'([1-5])형\(([^)]+)\)',leaf)
  if kind:
   own=re.search(r'[①-⑤]\s*'+kind[1]+r'형\([^)]*\)(.*?)(?=[①-⑤]\s*[1-5]형|⑥|$)',raw,re.S)
   target='피보험자가 '+kind[1]+'형의 '+kind[2].replace('납입면제형','')+'에 해당하는 약관상 진단확정을 받은 경우의 보험료 납입면제 보장입니다.'
   cond=['이 행은 '+kind[1]+'형에만 적용하며 다른 형의 사유·대상계약은 적용하지 않습니다. '+short(own[1]) if own else '해당 형의 납입면제 사유와 대상계약을 적용합니다.']
   if '암' in kind[2] and '90일' in co(raw):cond.append('암 납입면제 보장개시는 최초계약일(부활 시 부활일)부터 그 날을 포함하여 90일 경과 다음 날입니다. 약관상 암 제외범위를 적용합니다.')
  else:
   target='피보험자가 해당 납입면제 특약의 약관상 사유를 충족한 경우 보험료 납입을 면제합니다. '+short(cause.split('용어')[0])
 if '선지급' in n or '사후정리' in n or '양육연금' in n:
  cond.append('기존 사망보험금의 선지급·지급 방식 변경이며 별도의 추가 사망보험금이 아닙니다.')
 if '소액암진단특약' in n:
  cond=['해당 특약에 가입하고 담보명에 해당하는 질병으로 약관상 진단확정되어야 합니다. 최초 1회 지급하며 최초계약일부터 1년 미만은 약정 보험금의 50%를 지급합니다. 갱신계약에서 이미 지급된 동일 질병의 잔존·재발·전이에는 지급하지 않습니다. 지급사유 후 최초 갱신계약 보장개시일부터 5년 동안 추가 진단(단순 건강검진 제외)·치료 사실이 없으면 해당 기간 이후 약관상 보장 재개 기준을 적용합니다. 부활 시 해당 5년 기준일은 부활 청약일을 적용합니다. 사망 후 해당 질병이 직접 사인으로 확인된 경우 사망일을 진단확정일로 인정합니다.']
 if x['id']==1:
  cond=['전환 전 계약 지급금의 전부 또는 일부를 일시납하고 계약해당일부터 보장합니다. 연금개시는 보장개시일부터 5년 경과한 계약해당일입니다. 매년 계약해당일 생존 시 지급하며 선택한 보증기간은 10년(10회)·20년(20회)·30년(30회) 또는 100세입니다. 보증기간 중 사망 시 잔여 보증연금을 매년 지급하거나 공시이율로 할인하여 일시금 지급할 수 있습니다. 신청 시 잔여 보증기간 전부 또는 일부(연단위)를 할인 선지급할 수 있습니다. 연금개시 전 사망 시 사망 당시 계약자적립액을 지급합니다. 공시이율 변경에 따라 연금액이 변동되며 계약관리비용 공제를 반영합니다.']
 if x['id']==2:
  cond=['전환 전 계약 지급금의 전부 또는 일부를 일시납하고 계약해당일부터 보장합니다. 연금개시는 보장개시일부터 5년 경과한 계약해당일입니다. 연금개시 이후 최초 장기요양 1~3등급 판정 후 매년 계약해당일 생존 시 최대 10회 지급합니다. 보장개시 이후 연금개시 전 최초 1~3등급 판정을 받고 연금개시일에 생존한 경우 연금개시일부터 지급합니다. 노인장기요양보험법상 장기요양급여 제한을 받은 경우 지급하지 않습니다. 공시이율 변경에 따라 연금액이 변동되며 계약관리비용 공제를 반영합니다.']
 target=target.replace('피보험자에 대해 피보험자가','피보험자가')
 if '기준' in x['coverage_amount']:amount+=' 기준가입금액은 공시 지급표의 기준이며 실제 지급액은 가입한 금액을 적용합니다.'
 out.append({**x,'coverage_target':clean(target),'coverage_amount':clean(amount),'coverage_conditions':' '.join(dict.fromkeys(cond)),'updated_at':now})
(p/'revised.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print('rows',len(out),'conditions mean',round(statistics.mean(len(x['coverage_conditions']) for x in r)),round(statistics.mean(len(x['coverage_conditions']) for x in out)))
print('long',[(x['id'],len(x['coverage_target']),len(x['coverage_conditions'])) for x in out if len(x['coverage_target'])>1200 or len(x['coverage_conditions'])>3000][:20])
