import json,re,shutil,statistics
from pathlib import Path
from datetime import datetime,timezone,timedelta
p=Path('work/aig/revision');p.mkdir(exist_ok=True)
if not (p/'original.xlsx').exists():shutil.copy2('C:/Users/FAS/Desktop/데이터분석/AIG손해보험_2507_담보분석.xlsx',p/'original.xlsx')
r=json.loads(Path('work/aig/records.json').read_text(encoding='utf8'));sections=json.loads(Path('work/aig/sections.json').read_text(encoding='utf8'))
def co(s):return re.sub(r'\s+','',s)
terms=['보험가입금액','보험계약일','최초계약일','계약일','지급사유','지급금액','보장개시일','갱신계약','갱신일','피보험자','보험수익자','보험기간','요양병원','상급종합병원','제자리암','경계성종양','기타피부암','갑상선암','진단확정','직접적인','입원일수','간병인사용','간호·간병통합서비스','항암방사선','항암약물','표적항암약물허가치료','보장하지','지급하지','그날','포함하여','다음날','지난날','최초','제외','해당액','계속입원','사용일수','장해지급률']
def clean(s):
 s=re.sub(r'\s+',' ',s.replace('\x00','')).strip()
 for t in terms:s=re.sub(r'\s*'.join(map(re.escape,t)),t,s)
 s=re.sub(r'제\s*\d+조\s*\([^)]*\)(?:\s*제\d+항)?','',s)
 s=re.sub(r'제\d+항(?:\s*및\s*제\d+항)?(?:에 따라|을 적용합니다|의)?','',s)
 return re.sub(r'\s+',' ',s).strip(' .;')
def section(x):return next(s for s in sections[x['doc']] if s['name']==x['policy_name'])
now=datetime.now(timezone(timedelta(hours=9))).isoformat(sep=' ',timespec='seconds');out=[]
for x in r:
 s=section(x);d=clean(x['description']);n=co(x['name']);detail=s['articles'].get('보험금지급에관한세부규정','');dt=co(detail)
 event=d.split('구분 지급금액')[0].split('※')[0]
 event=re.sub(r'보장개시일.*?이후에?\s*','',event)
 event=re.split(r'보험가입금액|아래의 금액|아래 금액',event)[0]
 event=re.sub(r'최초\s*1회.*$','',event).strip(' ✓,.;')
 if not event:event=clean(s['articles'].get('보험금의지급사유','')).split('지급금액')[0]
 target='해당 계약의 피보험자가 '+event+'에 해당하는 경우를 보장합니다.'
 if n.startswith('[갱신형]유사암진단'):target='피보험자의 제자리암·경계성종양·기타피부암·갑상선암 진단확정을 보장합니다.'
 if n.startswith('[갱신형]소액암진단'):target='피보험자의 전립선암·유방암·자궁암·방광암 진단확정을 보장합니다.'
 if '일반암(소액암제외)진단' in n:target='피보험자의 약관상 일반암 진단확정을 보장합니다. 소액암(전립선암·유방암·자궁암·방광암)과 유사암(기타피부암·갑상선암·제자리암·경계성종양)은 제외합니다.'
 target=target.replace('경우에 해당하는 경우를','경우를').replace('확정시 에 해당하는 경우를','확정되는 경우를')
 event=re.split(r'경우에는|경우|받았을 때|받았을때|받게 된|확정시|되었을 때',event)[0].strip(' ,')
 target='피보험자가 '+event+'인 경우를 보장합니다.'
 if '진단비' in n:
  risk=re.sub(r'\[갱신형\]|\((?:305간편심사형|간편심사)\)','',x['name']).split('진단비')[0].strip()
  if '림프절전이암' in n:risk='림프절전이암'
  elif '특정전이암' in n:risk='특정전이암'
  target='피보험자의 약관상 '+risk+' 진단확정을 보장합니다.'
  if '유사암' in n:target='피보험자의 제자리암·경계성종양·기타피부암·갑상선암 진단확정을 보장합니다.'
  elif '소액암진단' in n:target='피보험자의 전립선암·유방암·자궁암·방광암 진단확정을 보장합니다.'
  elif '일반암(소액암제외)' in n:target='피보험자의 일반암 진단확정을 보장합니다. 전립선암·유방암·자궁암·방광암과 기타피부암·갑상선암·제자리암·경계성종양은 제외합니다.'
 if '사용' in n and '입원일당' in n:
  place='요양병원' if '요양병원,' in n else '요양병원을 제외한 병원' if '간호·간병' in n else '요양병원을 제외한 병원·의원'
  service='간호·간병통합서비스' if '간호·간병' in n else '약관상 간병인'
  target=f'피보험자가 암·기타피부암·갑상선암·제자리암·경계성종양 치료를 위해 {place}에 입원하여 {service}을 실제 사용한 날을 보장합니다.'
 if '질병80%' in n:target='피보험자가 보험기간 중 진단확정된 질병으로 약관 장해분류표상 장해지급률 80% 이상인 상태가 된 경우를 보장합니다.'
 if '질병사망' in n:target='피보험자가 보험기간 중 질병으로 사망한 경우를 보장합니다.'
 target=target.replace('받은 인 경우','받은 경우').replace('확정되고,인 경우','확정된 경우')
 for a,b in {'받은인 경우':'받은 경우','받았을인 경우':'받은 경우','수술을인 경우':'수술을 받은 경우','치료를인 경우':'치료를 받은 경우','입원한인 경우':'입원한 경우','서비스을':'서비스를','치 료':'치료','목 적':'목적','목적으 로':'목적으로','약관에 서':'약관에서'}.items():target=target.replace(a,b)
 if '입원비' in n:
  risk='고액치료비암' if '고액치료비암' in n else '전이암' if '전이암' in n else '암·기타피부암·갑상선암·제자리암·경계성종양'
  place='상급종합병원' if '상급종합병원' in n else '요양병원' if '요양병원암' in n else '요양병원을 제외한 병원·의원'
  target=f'피보험자가 {risk}으로 진단확정되고 해당 질병 치료를 위해 {place}에 1일 이상 입원한 경우를 보장합니다.'
 amount=clean(x['amount']).replace('：',': ')
 if amount.startswith('보험증권에 기재된 해당 담보 보험가입금액(계약별 결정)'):
  amount=amount.replace('보험증권에 기재된 해당 담보 보험가입금액(계약별 결정)','보험증권에 기재된 해당 담보 가입금액의 100%를 지급합니다. 가입금액은 계약별로 정해집니다.')
 if '입원비' in n or '입원일당' in n:
  unit='실제 간병인·간호간병서비스 사용 1일당' if '사용' in n else '입원 1일당'
  amount=unit+' 지급액입니다. '+amount
 elif '통원비' in n:amount='통원 1회당 지급액입니다. '+amount
 else:amount='해당 담보의 보험금 지급기준입니다. '+amount
 reduction=re.search(r'(\d+)년\s*미만.{0,70}?(\d+(?:\.\d+)?%)',d)
 if reduction and reduction[2] not in amount:amount+=' 최초계약일 후 '+reduction[1]+'년 미만에는 '+reduction[2]+'를 지급합니다.'
 cond=['해당 담보 가입 및 보험기간 중 약관상 지급사유 충족 시 적용합니다.']
 if '90일' in dt and '보장개시일' in dt and '재진단' not in n:
  cond.append('암 보장개시는 최초 보험계약일부터 그 날을 포함하여 90일이 지난 다음 날이며, 갱신계약은 갱신일부터 보장합니다.')
  first=co(re.split(r'[②-⑳]',detail)[0])
  if all(z in first for z in ['기타피부암/','보험계약일']):
   risks=[z for z in ['기타피부암','갑상선암','제자리암','경계성종양'] if z in first]
   cond.append('·'.join(risks)+'의 보장개시는 보험계약일이며, 갱신 시 갱신일입니다.')
  if '부활' in dt:cond.append('부활 시 부활일을 최초계약일로 보아 보장개시일을 다시 적용합니다.')
 if reduction:
  percentages=re.findall(r'\d+(?:\.\d+)?%',amount)
  if len(set(percentages))>2:cond.append('최초계약일 후 '+reduction[1]+'년 미만은 질병 구분에 따라 감액 지급합니다. 질병별 지급비율은 보장금액의 '+', '.join(dict.fromkeys(percentages))+' 기준을 적용하며 갱신계약은 갱신 지급표를 따릅니다.')
  else:cond.append('최초계약일 후 '+reduction[1]+'년 미만 지급사유는 보험가입금액의 '+reduction[2]+'를 지급합니다. 갱신계약은 해당 지급표의 갱신 기준을 적용합니다.')
 if '각각1회' in co(d) or '각각최초1회' in co(d):cond.append('약관에서 구분한 질병·치료별 각각 최초 1회 한도입니다.')
 elif '최초1회' in co(d) or '최초1회' in n:cond.append('최초 1회 한도로 지급합니다.')
 for z in re.findall(r'연간\s*\d+\s*회',d+' '+x['name']):
  q=co(z)+' 한도입니다.'
  if q not in cond:cond.append(q)
 if '1일1회' in co(d) or '1일1회' in n:cond.append('같은 날은 1회만 지급합니다.')
 limit=re.search(r'(\d+)일(?:한도|을한도)',co(d+' '+x['name']))
 if limit and ('입원' in n):cond.append('1회 입원당 '+limit[1]+'일 한도입니다.')
 if '요양병원제외' in n:cond.append('요양병원 입원은 제외합니다.')
 if '급여' in n:cond.append('국민건강보험 급여에 해당하는 약관상 치료만 보장합니다.')
 # Retain benefit-specific restrictions from complete policy paragraphs;
 # leave diagnostic disputes and claim procedures in the source document.
 for key,value in s['articles'].items():
  if '세부규정' not in key and '지급하지않는' not in key:continue
  for b in re.split(r'[①-⑳]',value):
   t=co(b)
   if len(t)<15 or any(v in t for v in ['보장개시일은아래','부활된경우','합의하지못할','제3자','연명의료','보통약관제1절일반조항제5조']):continue
   if not any(v in t for v in ['차감','지급하지','제외','한도','합하여','180일이경과','365일','허가','승인','재진단','종류','계속보장','인정하지','동일한']):continue
   b=re.split(r'\[[^]]*예시[^]]*\]|<[^>]*예시[^>]*>',b)[0]
   b=b.split('용어풀이')[0]
   if '보험기간중' in t and '사망' in t and '차감' in t:b='보험기간 중 사망 후 해당 질병이 직접 사인임이 확인되면 사망일을 진단확정일로 봅니다. 이미 지급한 계약자적립액은 보험금에서 차감합니다.'
   elif '효능효과' in t and '승인' in t:b='식약처 허가 효능·효과 내 사용 또는 암질환심의위원회 심의 후 심평원이 승인한 해당 요양기관의 요법에 한해 보장합니다.'
   elif '허가치료' in t and '처방일자' in t:b='약물을 실제 투여한 경우를 보장하며 최초 처방일을 기준으로 합니다. 안전성·유효성 인정 범위 변경 시 변경 후 최초 처방일을 적용합니다.'
   elif '각입원일수' in t and '합하여' in t:b='같은 질병으로 반복 입원하거나 전원하면 1회 입원으로 보아 일수를 합산합니다.'
   elif '계속보장' in t and '보험기간이끝났' in t:b='보장개시 후 치료 중 보험기간이 끝나도 퇴원 전 계속입원은 약관상 한도 내에서 보장합니다.'
   elif '의사의지시' in t:b='정당한 이유 없이 의사 지시를 따르지 않으면 보험금 전부 또는 일부를 지급하지 않습니다.'
   elif '실제사용한날' in t:b='해당 간병서비스를 실제 사용한 날만 합산하며 사용하지 않은 날은 지급하지 않습니다.'
   elif '선천성기형' in t:b='선천성기형·선천적질환, 알코올중독·습관성 약품·환각제 사용, 건강검진·예방접종·보신용 투약 등 약관상 제외사유는 보장하지 않습니다.'
   if '180일이경과' in t and '입원' in n:
    anchor='보험금이 지급된 최종입원의 퇴원일' if '최종입원의퇴원일' in t else '보험금이 지급된 최종 간병서비스 사용일'
    b=anchor+'부터 180일이 경과하여 시작한 입원은 새로운 입원으로 봅니다. 퇴원 없이 계속 입원하는 경우는 약관상 간주 퇴원일과 180일의 보장 재개 기준을 적용합니다.'
   elif '365일' in t and '누적' in t:b='같은 질병의 누적 지급일수가 365일을 초과하면 최종 갱신계약 만료일까지 추가 지급하지 않습니다. 해당 질병 완치 후 다시 진단된 경우는 다른 질병으로 봅니다.'
   elif '간병인을실제사용' in t:b='간병인을 실제 사용한 날만 합산하며, 사용하지 않은 날은 지급하지 않습니다.'
   elif '간병인사용' in n and '간호·간병통합서비스' in t and '지급하지' in t:b='간호·간병통합서비스를 제공받은 경우 간병인사용 일당은 지급하지 않습니다.'
   b=clean(b)
   b=re.sub(r'^(?:의|에서|에 따라)\s*','',b)
   if '입원' in n and '지급일수는1회입원당' in t:continue
   if b and b not in cond:cond.append(b+'.')
 if '※' in d:
  for b in d.split('※')[1:]:
   if '제외' in b or '지급하지' in b:
    b=b.split('구분 지급금액')[0]
    if clean(b)+'.' not in cond:cond.append(clean(b)+'.')
 if '질병사망' in n:cond.append('고의 자해·고의 가해 등 보통약관상 지급 제외사유와 예외를 적용합니다.')
 if '재진단암진단' in n:
  target='피보험자가 첫 번째 암 진단 후 약관상 재진단암으로 진단확정된 경우를 보장합니다. 기타피부암·갑상선암·전립선암은 제외합니다.'
  cond=['해당 담보 가입 및 보험기간 중 재진단암 진단확정 시 적용합니다. 첫 재진단암은 첫 번째 암 진단일부터, 두 번째 이후는 직전 재진단암 진단일부터 각각 그 날을 포함하여 2년이 지난 다음 날부터 보장합니다. 해당 2년 이내 진단은 지급하지 않습니다. 보험기간 중 사망 후 해당 암이 직접 사인임이 확인되면 사망일을 진단확정일로 보며 이미 지급한 계약자적립액은 차감합니다.']
 amount=amount.replace('정해집니다.;','정해집니다.').replace(';','; ')
 cond=list(dict.fromkeys(cond))
 out.append({**x,'target':target,'amount':amount,'conditions':' '.join(cond),'updated_at':now})
(p/'revised.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print('rows',len(out),'conditions mean',round(statistics.mean(len(x['conditions']) for x in r)),round(statistics.mean(len(x['conditions']) for x in out)))
print('long',[(x['id'],len(x['conditions'])) for x in out if len(x['conditions'])>1600])
