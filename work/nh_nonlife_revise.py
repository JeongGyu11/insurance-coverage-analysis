import json,re,shutil,statistics
from pathlib import Path
from datetime import datetime,timezone,timedelta
p=Path('work/nh_nonlife/revision');p.mkdir(exist_ok=True)
if not (p/'original.xlsx').exists():shutil.copy2('C:/Users/FAS/Desktop/데이터분석/NH농협손해보험_2507_담보분석.xlsx',p/'original.xlsx')
r=json.loads(Path('work/nh_nonlife/records.json').read_text(encoding='utf8'));S=json.loads(Path('work/nh_nonlife/sections.json').read_text(encoding='utf8'))
def co(s):return re.sub(r'\s+','',s)
terms=['보험가입금액','보험계약일','보장개시일','최초계약','보험기간','보험증권','장해지급률','장해분류표','후유장해','피보험자','진단확정','직접적인','최초','지급하지','보상하지','자기부담금','보상한도','보상비율','반려동물','요양병원','기타피부암','갑상선암','제자리암','경계성종양','입원일수','상급종합병원','간병인','농협손해보험']
def clean(s):
 s=re.sub(r'\s+',' ',s.replace('\x00','')).strip()
 s=re.sub(r'-\s*\d+\s*-',' ',s)
 s=re.sub(r'▶[^①②③④⑤⑥⑦⑧⑨⑩]{0,100}?약관',' ',s)
 s=re.sub(r'(?:\(무\)|무배당)\s*(?:NH|헤아림).{0,90}?(?:특별약관|보통약관|약관)(?:\s*\d종\([^)]*\))?(?:\s*보통약관)?\s*[◀▶]*',' ',s)
 for a in terms:s=re.sub(r'\s*'.join(map(re.escape,a)),a,s)
 s=s.replace('보험보험증권에 기재된 해당 보장 보험가입금액','보험증권에 기재된 해당 보장 보험가입금액')
 s=s.replace('해당 세부보장 보험증권에 기재된 해당 보장 보험가입금액','해당 세부보장 보험가입금액')
 return re.sub(r'\s+',' ',s).strip(' .;')
def concise(s):
 s=clean(s)
 # Remove balanced article citations without damaging nested medical names.
 s=re.sub(r'제\s*\d+조(?:의\d+)?\s*\([^()]*(?:\([^()]*\)[^()]*)*\)(?:\s*제\d+항)?','',s)
 s=re.sub(r'제\d+항(?:\s*내지\s*제\d+항)?(?:에서 정한|에 따른)?','',s)
 s=re.sub(r'\(이하[^)]*\)','',s)
 s=s.split('【예시')[0].split('<예시')[0].split('[예시')[0].split('용어풀이')[0]
 s=re.sub(r'^(?:의|에서|에 따라)\s+','',s)
 return re.sub(r'\s+',' ',s).strip(' .;')
def parts(s):return re.split(r'[①-⑳㉑-㉟]',s)
now=datetime.now(timezone(timedelta(hours=9))).isoformat(sep=' ',timespec='seconds');out=[]
for x in r:
 n=x['coverage_name'];d=clean(x['raw']['cause']);amount=clean(x['coverage_amount']);pet='펫앤미' in x['product_name'];maternal='부양자' in x['coverage_target'];basic=x['type']=='기본계약'
 key={'doc1':'doc3' if '종합형' in x['product_name'] else 'doc2','doc5':'doc6','doc8':'doc9','doc11':'doc12','doc14':'doc15'}[x['raw']['key']]
 section=next((a for a in S[key] if a['name']==x['source_name']),None)
 event=d.split('※')[0]
 event=re.sub(r'\([^)]*(?:최초|연간|한도|1회|1일)[^)]*\)','',event)
 event=re.sub(r'^(?:피보험자가|보험기간 중에?|보장개시일 이후에?)\s*','',event)
 event=re.sub(r'(?:보험가입금액|가입금액).*','',event)
 subject='약관에서 정한 부양자·산모 또는 해당 특약의 피보험자' if maternal else '보험증권에 기재된 반려동물('+('고양이' if '고양이' in x['product_name'] else '강아지')+') 및 해당 보장의 반려인' if pet and '반려동물' in n else '해당 계약의 피보험자'
 target=subject+'에 대해 '+event.strip(' .')+'를 보장합니다.'
 target=target.replace('경우를 보장','경우를 보장').replace('사망시를','사망한 경우를').replace('경우를','경우를')
 if pet and '치료비' in n:
  risk='피부질환(외이염·중이염·피부알러지·피부트러블 포함)' if '피부질환' in n else '약관상 구강질환' if '구강질환' in n else '약관상 상해 또는 질병'
  target='보험증권에 기재된 '+('고양이' if '고양이' in x['product_name'] else '강아지')+'의 '+risk+' 치료를 위해 실제 부담한 동물병원 치료비를 보장합니다.'
 if '배상책임' in n:target=subject+'가 '+event.strip(' .')+'에 따른 법률상 배상책임을 보장합니다.'
 if '가족일상생활' in n:target='약관상 본인·가족이 일상생활 중 타인에게 신체 장해(대인) 또는 재물손해(대물)를 입혀 부담하는 법률상 배상책임을 보장합니다.'
 if '위탁비용' in n:target='피보험자에게 약관상 위탁사유가 발생하여 보험증권의 반려동물을 위탁할 때 실제 부담한 위탁비용을 보장합니다. 세부 위탁사유는 해당 특약을 적용합니다.'
 # Keep monetary clauses and units intact, explaining their contractual basis.
 if pet and '치료비' in n:intro='실제 보상대상 동물병원 치료비에서 증권상 자기부담금을 차감한 후 보상비율을 적용하여 한도 내 지급합니다. '
 elif '배상책임' in n or '법률비용' in n or '위탁비용' in n or '벌금' in n:intro='약관상 보상대상 손해·비용을 증권의 보상한도 내에서 지급합니다. '
 else:intro='보험증권에 기재된 해당 담보 가입금액을 기준으로 아래 지급비율·단위·횟수를 적용합니다. '
 amount=intro+amount
 cond=['보험기간 중 해당 담보에 가입하고 약관상 지급사유를 충족해야 합니다.']
 for limit in re.findall(r'\([^)]*(?:최초|연간|한도|\d+일|\d+회|진단후)[^)]*\)',d+' '+x['coverage_amount']):
  q=concise(limit).strip('()')
  if q and q not in cond:cond.append(q+'.')
 for note in d.split('※')[1:]:
  q=concise(note)
  if q:cond.append(q+'.')
 articles=section['articles'] if section else []
 if basic:
  articles=articles+[{'title':'세부규정','text':line.split(':',1)[-1]} for line in x['coverage_conditions'].split('\n') if line.startswith('기본계약')]
 if articles:
  for a in articles:
   title=co(a['title'])
   if not any(z in title for z in ['세부규정','지급하지','보상하지','보장개시','한도','자기부담','정의','보장별보험금']):continue
   for block in parts(a['text']):
    t=co(block)
    if len(t)<12 or any(z in t for z in ['합의하지못','제3자','법률이개정','관련법령등의개정','개정에따라수가코드','용어의정의는','연명의료중단','평균공시이율은','의료기관은다음','계약자는회사가정한']):continue
    if not any(z in t for z in ['보장개시','지급하지','보상하지','차감','공제','한도','최초','연간','1회','중복','갱신','동일한','365일','180일','허가','승인','급여','제외']):continue
    if any(z in title for z in ['정의']) and not any(z in t for z in ['제외','허가','승인','보장개시','90일','30일','지급하지','급여']):continue
    q=concise(block)
    if not q:continue
    # Retain operative sentences, leaving legal definitions and examples in sources.
    if len(q)>650:
     sentences=re.split(r'(?<=다\.)\s+',q)
     selected=[z for z in sentences if any(w in co(z) for w in ['보장개시','지급하지','보상하지','차감','공제','한도','최초','연간','중복','365일','180일','90일','30일','보험나이','15세','허가','승인','제외']) and not any(w in co(z) for w in ['예시','가령','제3자','의료기관이란','법률의성립','다음과같이구분'])]
     q=' '.join(selected)
    if q and co(q) not in {co(z.rstrip('.')) for z in cond}:cond.append(q.rstrip('.')+'.')
 if pet and '치료비' in n:
  cond.append('질병은 최초계약일부터 30일이 지난 다음 날부터, 상해는 최초계약일부터 보장합니다. 구강·피부 등 확장담보는 기본 치료비와 합산한 한도이며 별도 한도를 추가하지 않습니다.')
 if maternal:cond.append('해당 모성 특약의 부양자·산모 범위와 임신·출산 관련 보장기간을 적용합니다.')
 if basic:
  old=co(x['coverage_conditions'])
  cond=['보험기간 중 해당 지급사유를 충족해야 합니다.']
  for limit in re.findall(r'\([^)]*(?:최초|한도|1회)[^)]*\)',d+' '+x['coverage_amount']):cond.append(concise(limit).strip('()')+'.')
  if '암진단비' in n:
   amount+=' 최초계약은 계약일부터 1년 미만 50%, 1년 이상 100%를 지급하며 갱신계약은 100%를 지급합니다.'
   cond.append('암 보장개시는 최초계약일부터 그 날을 포함하여 90일 경과 다음 날이며 갱신계약은 갱신일입니다. 최초 1회 지급합니다. 기타피부암·갑상선암 등 유사암 및 전암상태는 해당 암 분류에서 제외합니다.')
   if '부활' in old:cond.append('부활 시 약관상 보장개시일을 다시 적용합니다.')
  if '후유장해' in n:
   cond.append('해당 담보에서 정한 상해 원인과 장해지급률 구간을 충족해야 합니다. 장해지급률은 약관 장해분류표에 따라 판정하며 같은 부위의 복수 장해는 높은 지급률을 적용합니다.')
   if '180일' in old:cond.append('장해가 180일 내 확정되지 않으면 사고일부터 180일째 의사진단을 기준으로 하되 약관의 별도 판정시기를 적용합니다.')
   if '한시장해' in old and '5년' in old and '20%' in old:cond.append('5년 이상 한시장해는 해당 장해지급률의 20%를 적용합니다.')
  if '사망' in n:cond.append('운전자·비운전자·대중교통 이용 중 등 해당 담보의 교통상해 범위를 충족해야 합니다. 고의 가해 등 약관상 지급 제외사유와 예외를 적용합니다.')
 if '항암방사선치료비' in n and '20%' in amount and '기타피부암' in d and '갑상선암' in d:
  amount='일반암(기타피부암·갑상선암 제외)은 해당 가입금액, 기타피부암·갑상선암은 각각 가입금액의 20%를 지급하는 구분입니다. '+amount
 if '갱신형가족일상생활중배상책임' in n:
  cond=['보험기간 중 약관상 본인·가족의 일상생활 사고로 법률상 배상책임이 발생해야 합니다. 1사고당 증권상 가입금액 한도로 보상합니다. 자기부담금은 대인 없음, 대물 누수사고 50만원, 누수 외 대물사고 20만원입니다. 하나의 사고로 대인·대물 누수·대물 기타가 동시에 발생하면 각각의 사고로 보아 한도와 공제를 적용합니다. 고의, 직무 수행, 증권상 주택 외 부동산, 같은 세대 친족에 대한 책임, 자동차 등 약관상 제외사유를 적용합니다. 주택 공사 사고는 제외하되 통상적인 유지·보수 작업의 예외는 적용합니다.']
 if '납입면제' in n:amount='약관에서 정한 납입면제 사유 충족 시 해당 대상계약의 이후 보장보험료 납입을 면제합니다. 면제 범위와 갱신 후 적용은 해당 특약을 따릅니다.'
 seen=set();dedup=[]
 for q in cond:
  if co(q) not in seen:seen.add(co(q));dedup.append(q)
 cond=dedup
 out.append({**x,'coverage_target':target,'coverage_amount':amount,'coverage_conditions':' '.join(dict.fromkeys(cond)),'updated_at':now})
(p/'revised.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print('rows',len(out),'condition avg',round(statistics.mean(len(x['coverage_conditions']) for x in r)),round(statistics.mean(len(x['coverage_conditions']) for x in out)))
print('long conditions',[(x['id'],x['coverage_name'],len(x['coverage_conditions'])) for x in out if len(x['coverage_conditions'])>3500][:15])
