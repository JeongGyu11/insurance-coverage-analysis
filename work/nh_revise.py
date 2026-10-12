import json,re,shutil,statistics
from pathlib import Path
from datetime import datetime,timezone,timedelta
p=Path('work/nh/revision');p.mkdir(exist_ok=True)
if not (p/'original.xlsx').exists():shutil.copy2('C:/Users/FAS/Desktop/데이터분석/NH농협생명_2507_담보분석.xlsx',p/'original.xlsx')
r=json.loads(Path('work/nh/records.json').read_text(encoding='utf8'))
def co(s):return re.sub(r'\s+','',s)
def clean(s):
 s=re.sub(r'\s+',' ',s).strip()
 for t in ['농업작업안전재해','농업작업안전질병','장해지급률','장해분류표','장해상태','신체부위','최초','피보험자','보험기간','특정감염병','특정질병','진단확정','직접목적','사망','해당일','깁스치료','부목','입원일수']:
  s=re.sub(r'\s*'.join(map(re.escape,t)),t,s)
 return s
now=datetime.now(timezone(timedelta(hours=9))).isoformat(sep=' ',timespec='seconds');out=[]
for x in r:
 n=x['coverage_name'];raw=x['coverage_conditions'];t=co(raw);amount=clean(x['coverage_amount']);medical=n.startswith('상해·질병치료급여금');rider=x['id']>=77;holiday='휴일보장형' in x['type']
 if medical:
  risk='농업작업안전재해' if '(상해' in n else '농업작업안전질병' if '(질병' in n else '농업작업안전재해 또는 농업작업안전질병'
  action='입원치료' if '(상해입원)' in n or '(질병입원)' in n else '외래치료와 처방조제' if '통원(외래' in n else '비급여 도수치료·체외충격파치료·증식치료' if '도수치료' in n else '비급여 주사치료' if '주사료' in n else '비급여 자기공명영상진단(MRI/MRA, 조영제·판독료 포함)'
  target=f'가입 자격을 충족한 피보험자가 {risk}의 치료를 위해 받은 {action}의 실제 본인부담 의료비를 보장합니다.'
  amount='실제 보상대상 의료비에서 약관상 자기부담금을 공제한 후 한도 내 지급하는 실손 보장입니다. '+amount
  if '적용받지못하는' in t and '40%' in t:amount+=' 국민건강보험·의료급여 미적용 시 약관상 본인부담 의료비의 40%를 해당 한도 내 보상합니다.'
  cond=['치료급여금 기본형에 가입해야 하며 부(不)담보형은 보장하지 않습니다. 농업작업안전재해·농업작업안전질병의 범위는 약관 분류표에 따릅니다. 다수의 실손보험이 있으면 실제 보상대상 의료비를 초과하지 않도록 약관상 비례분담을 적용합니다.']
  if '비급여' not in n:cond.append('비급여 도수·체외충격파·증식치료, 비급여 주사료, 비급여 MRI/MRA는 기본 의료비에서 제외하고 각 별도 보장 기준을 적용합니다.')
  if '180일' in t:
   cond.append('보험기간 종료 시 계속 치료 중이면 종료일을 제외하고 180일까지 약관상 연장 보상을 적용합니다. 동일 상품에 연속 재가입하면 해당 재가입 조항을 적용합니다.')
   if '비급여' in n:cond.append('종료 후 연장보상 한도는 직전 보험기간의 연간 한도에서 기지급액을 차감한 잔액입니다.')
  if '90회' in t and '통원' in n:cond.append('계약 종료 후 연장보상의 외래·처방조제는 각각 90회·90건 한도를 적용합니다.')
  if '275일' in t:cond.append('입원 의료비 5,000만원 한도 소진 시 한도종료일부터 90일 경과 후 한도를 복원합니다. 최초입원 후 275일 이내 소진한 경우는 최초입원일부터 365일 경과 후 복원하며 계약 종료 후 연장보상에는 해당 복원 규정을 적용하지 않습니다.')
  if '도수치료' in n or 'MRI/MRA' in n:cond.append('한 번의 입원·통원에서 복수 치료·진단을 받으면 약관에서 정한 각 치료·진단행위별로 공제금액과 한도를 적용합니다.')
  if '주사료' in n and '식품의약품안전처' in t:cond.append('주사제의 약관상 허가·안전성·유효성 인정 범위를 적용합니다.')
  exclusions=['고의 가해','예방·미용 목적 치료']
  if '상습' in t:exclusions.append('상습적 유독물질 흡입·섭취 및 세균성 음식물중독')
  if '치과' in t and '한방' in t:exclusions.append('약관에서 제외한 치과·한방 비급여')
  cond.append('주요 제외사항은 '+', '.join(exclusions)+' 등입니다. 임신·출산 등 제외사유와 약관에서 명시한 예외를 적용합니다.')
 else:
  cause=clean(raw.split('\n')[1]);event=re.sub(r'\([^)]*(?:최초|한도)[^)]*\)','',cause)
  event=event.replace('피보험자가 ','').replace('이 특약의 ','')
  for a,b in [('확정되었을 때','확정된 경우'),('되었을 때','된 경우'),('하였을 때','한 경우'),('받았을 때','받은 경우'),('발생한 때','발생한 경우'),('받은 때','받은 경우')]:event=re.sub(re.escape(a)+r'$' ,b,event)
  target='가입 자격을 충족한 피보험자가 '+event.rstrip(' .')+'에 해당하는 경우를 보장합니다.'
  target=target.replace('경우에 해당하는 경우','경우').replace('한 경우에 해당하는 경우','한 경우')
  if amount.startswith('[1구좌 기준]'):amount=amount.replace('[1구좌 기준]','1구좌 기준 지급액입니다. 실제 지급액은 계약의 가입형과 가입내용을 적용합니다.')
  elif amount.startswith('['):amount=re.sub(r'^\[([^]]+)\]',r'\1 지급액입니다. 실제 계약가입금액을 적용합니다.',amount)
  if '× 장해지급률' in amount:amount+=' 해당 형의 기준금액에 약관상 장해지급률을 곱하여 지급합니다.'
  if rider:cond=[clean(raw.split('\n')[0])]
  else:cond=['보험기간 중 해당 담보의 지급사유를 충족해야 합니다.'+(' 특정질병·특정감염병의 범위는 해당 약관 분류표에 따릅니다.' if n.startswith(('특정질병','특정감염병')) else ' 농업작업안전재해·농업작업안전질병은 약관상 농업작업 범위와 해당 분류표에 따릅니다.')]
  if '최초1회' in co(cause):cond.append('재해·질병 구분에 따라 각각 최초 1회 한도입니다.' if '각각' in cause else '최초 1회에 한하여 지급합니다.')
  if '장해' in n or '간병급여금' in n:
   cond.append('장해지급률은 약관 장해분류표에 따릅니다. 재해일 또는 질병 진단일부터 180일 내 확정되지 않으면 180일째 의사진단으로 판정하되 별도 판정시기를 정한 경우 그 기준을 적용합니다. 같은 원인의 여러 부위 장해는 합산하되 동일 부위 복수 장해는 높은 지급률을 적용합니다.')
   if '재해장해' in n:cond.append('기존·기지급 동일 부위 장해는 약관에 따라 차감하며 일반 3형은 해당 담보를 보장하지 않습니다.' if '일반형' in x['type'] else '기존·기지급 동일 부위 장해는 약관에 따라 차감합니다.')
   if '한시장해' in t and '5년' in t and '20%' in t:cond.append('5년 이상 한시장해는 해당 장해지급률의 20%를 적용합니다.')
  if '휴업(입원)' in n:cond.append('직접적인 치료를 목적으로 4일 이상 계속입원해야 하며 3일 초과분부터 1회 입원당 120일 한도로 지급합니다. 같은 재해·질병의 재입원·전원은 일수를 합산합니다. 최종 입원의 퇴원일부터 180일 경과 후 입원은 새 입원으로 보며 계속입원은 약관상 간주 퇴원일을 적용합니다. 만기 시 계속입원은 해당 120일 한도 내에서 보장합니다.')
  if '수술급여금' in n:
   cond.append('약관상 특정질병 치료를 위한 수술 1회당 지급합니다. 흡인·천자·신경차단 및 미용·피임·검사·진단 목적 수술 등은 약관상 수술에서 제외합니다.')
  if '특정감염병' in n:cond.append('약관 분류표상 특정감염병을 의사가 진단확정한 경우 진단 1회당 지급합니다.')
  if holiday:
   cond.append('휴일 여부는 사망일·진단일이 아닌 재해 발생일을 기준으로 합니다. 휴일은 토요일·일요일·근로자의 날·공휴일 등 약관 정의를 적용합니다.')
   if n.startswith(('유족급여금','장례비')):cond.append('SFTS(A93.80) 사망은 휴일 발생 여부로 지급을 제한하지 않습니다.')
   elif n.startswith('특정감염병'):cond.append('특정감염병 진단은 휴일 발생 여부로 지급을 제한하지 않습니다.')
  if rider:
   cond.append('온라인 상품은 특약을 부가할 수 없습니다.')
   if x['id']==77:cond.append('장제비지원특약의 조합원·영농 종사자 자격요건을 충족해야 하며 산림조합 자격만 충족한 경우는 제외합니다.')
   if x['id']==82:cond.append('치아파절은 제외합니다. 동일 재해로 복합골절이 생겨도 1회만 지급하며 의학적 처치·치료를 위해 골절시킨 경우는 지급하지 않습니다.')
   if x['id']==83:cond.append('부목(Splint Cast) 치료는 제외합니다. 동일 질병·재해로 반복 치료하거나 동시에 여러 부위를 깁스치료한 경우도 1회만 지급합니다.')
  if '사망' in n or n.startswith(('유족','장례','장제')):cond.append('고의 자해·고의 가해 등 지급 제외사유와 심신상실 등 약관상 예외를 적용합니다.')
 out.append({**x,'coverage_target':target,'coverage_amount':amount,'coverage_conditions':' '.join(cond),'updated_at':now})
(p/'revised.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print('revised',len(out),'conditions average',round(statistics.mean(len(x['coverage_conditions']) for x in r)),round(statistics.mean(len(x['coverage_conditions']) for x in out)))
