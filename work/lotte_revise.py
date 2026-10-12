import json,re,shutil,statistics
from pathlib import Path
from datetime import datetime,timezone,timedelta
p=Path('work/lotte/revision');p.mkdir(exist_ok=True)
shutil.copy2('C:/Users/FAS/Desktop/데이터분석/롯데손해보험_2507_담보분석.xlsx',p/'original.xlsx')
r=json.loads(Path('work/lotte/records.json').read_text(encoding='utf8'));ss=json.loads(Path('work/lotte/sections.json').read_text(encoding='utf8'))
def clean(t):
 t=re.sub(r'\s+',' ',t).strip()
 for w in ['피보험자','보험가입금액','보험기간','보험금','지급률','후유장해','진단확정','자기부담금','입원일당','보상한도','보험증권','직접적인','식중독','국내여행','보험료']:
  t=re.sub(r'\s*'.join(w),w,t)
 return t
def short(t):
 t=re.sub(r'<\s*용어풀이\s*>.*?(?=[②-⑳]|$)','',t,flags=re.S)
 t=re.sub(r'<[^>]*예시[^>]*>.*?(?=\n\s*\d+\.|[②-⑳]|$)','',t,flags=re.S)
 t=re.split(r'(?m:^【별표)',t)[0]
 t=re.sub(r'제\d+조\([^()]*(?:\([^()]*\)[^()]*)*\)(?:\s*제\d+항)?','',t)
 t=re.sub(r'\([^()]*(?:이하|이하에서)[^()]*\)','',t)
 return clean(t)
targets={1:'만 10세 이상 피보험자가 보이스피싱·피싱·파밍·스미싱·메모리해킹 등 약관상 금융사기로 입은 실제 금전적 손해. 요건을 충족하는 대면편취도 포함합니다.',2:'개인정보·신용도용으로 피보험자에게 발생한 약관상 직접적인 금전적 손실.',3:'개인정보·신용도용 피해로 피보험자가 부담한 약관상 법률비용.',4:'사이버폭력·스토킹 피해로 피보험자가 부담한 약관상 법률비용.',5:'사이버폭력·스토킹 피해로 피보험자가 부담한 약관상 심리상담·치료비용.',6:'사이버협박으로 피보험자에게 발생한 약관상 금전적 손해.',7:'개인정보 유출 피해로 피보험자가 부담한 약관상 법률비용.',22:'국내여행 중 급격하고 우연한 외래의 사고로 상해를 입고 그 직접적인 결과로 사망한 피보험자.',23:'국내여행 중 상해의 직접적인 결과로 장해분류표상 후유장해가 남은 피보험자.',45:'보험증권상 주거지에 보관된 약관상 보험목적에 발생한 도난손해.',46:'보험증권상 주거지 보험목적의 보관장소를 72시간 초과하여 약정 일수까지 비운 동안 발생한 도난손해.',50:'국내여행 중 발생한 질병의 직접적인 결과로 사망한 피보험자.',51:'국내여행 중 발생한 질병의 직접적인 결과로 장해지급률 80% 이상 고도후유장해가 남은 피보험자.',53:'국내여행 중 피보험자가 소유·휴대한 약관상 휴대품의 우연한 사고 손해. 단순 분실은 제외합니다.',64:r[63]['coverage_target'],65:r[64]['coverage_target'],72:'제주공항 국내선 출발 정기항공편을 유료승객으로 이용하려던 피보험자의 항공편 결항으로 발생한 추가 식음료비·교통비·숙박비.'}
medical={73:'피보험자의 상해 치료에 필요한 국민건강보험·의료급여 대상 급여 의료비 중 약관상 본인부담금.',74:'피보험자의 질병 치료에 필요한 국민건강보험·의료급여 대상 급여 의료비 중 약관상 본인부담금.',75:'피보험자의 상해 치료에 필요한 약관상 비급여 의료비. 3대비급여 치료는 별도 담보입니다.',76:'피보험자의 질병 치료에 필요한 약관상 비급여 의료비. 3대비급여 치료는 별도 담보입니다.',77:'피보험자가 상해·질병 치료를 목적으로 받은 약관상 비급여 도수치료·체외충격파치료·증식치료.',78:'피보험자가 상해·질병 치료를 목적으로 받은 약관상 비급여 주사료.',79:'피보험자가 상해·질병 치료를 목적으로 받은 약관상 비급여 자기공명영상진단(MRI/MRA), 조영제 및 판독료.'}
out=[];now=datetime.now(timezone(timedelta(hours=9))).isoformat(sep=' ',timespec='seconds')
for x in r:
 i=x['id'];n=x['coverage_name'];key='doc2' if 'guard' in x['product_name'] else 'doc5';s=next((z for z in ss[key] if z['name']==x['source_name']),None)
 pay=next((a['text'] for a in s['articles'] if a['title'] in ['보험금의 지급사유','보상하는 손해','보험금을 지급하는 사유']),'') if s else ''
 first=re.split(r'[②-⑳]',pay)[0];first=short(first)
 first=re.sub(r'^①?\s*회사는\s*','',first)
 first=re.split(r'지\s*급\s*사\s*유\s*소',first)[0]
 target=targets.get(i,medical.get(i,first or x['coverage_target']))
 if i==21:target=x['coverage_target']
 if i==70:target=targets[1]
 if i==71:target=targets[6]
 if i in [29,30,33,34,35,36]:
  target='국내여행 중 '+{'29':'교통사고','30':'교통사고','33':'강도 사고','34':'강도 사고','35':'약관상 스포츠단체 활동 사고','36':'약관상 스포츠단체 활동 사고'}[str(i)]+'로 상해를 입고 그 직접적인 결과로 '+('사망한' if '사망' in n else '장해분류표상 후유장해가 남은')+' 피보험자.'
 amount=('실제로 부담한 보상대상 손해·비용을 약정 한도·공제 기준에 따라 보상합니다. ' if any(z in n for z in ['비용','배상책임','금융사기','도용','사이버','손해','벌금','지원금','실손']) else '실제 가입한 해당 담보의 보험가입금액을 기준으로 지급합니다. ')+clean(x['coverage_amount'])
 cond=['보험증권에 기재된 가입 담보 및 보험기간·보장지역에 적용합니다.']
 if s and i<73:
  for a in s['articles']:
   if a['title'] not in ['보험금의 지급사유','보상하는 손해','보험금을 지급하는 사유','보상하지 않는 손해','보험금을 지급하지 않는 사유','보험금 지급에 관한 세부규정','보험금의 지급에 관한 세부규정','보험금 등의 지급한도','보험금의 지급한도','보험금의 비례분담','보상한도','보험금의 분담','의무보험과의 관계']:continue
   text=short(a['text'])
   if not text:continue
   if '세부규정' in a['title']:
    blocks=re.split(r'[①-⑳]',text)
    text=' '.join(b for b in blocks if not any(z in clean(b).replace(' ','') for z in ['제3자','합의하지못','연명의료','납입면제']))
   if text:cond.append(text)
  if key=='doc2':cond.append('총보상한도 설정 시 가입 담보 지급액 합계는 총한도 내이며, 1사고에 여러 담보 적용 시 가장 큰 자기부담금을 적용합니다. 총한도 미설정 시 담보별 자기부담금을 적용합니다.')
  else:cond.append('국내여행 중 보장하며 해당 특별약관의 변경·확장 사항을 우선 적용합니다. 그 외 보통약관의 고의·자해, 전쟁 등 해당 공통 면책을 적용합니다.')
 if i==21:cond=[x['coverage_conditions'].split('\n[보통약관')[0]]
 if i in [4,5]:
  cond=['대한민국 내 보험기간 중 사이버폭력·스토킹 피해에 대해 수사기관에 신고·고소·고발 등을 접수하고 가해자에게 검찰의 기소(약식기소 포함) 또는 기소유예 처분이 있어야 합니다. 다른 보험·보상제도·가해자로부터 보상받을 수 있는 금액은 공제합니다. 총보상한도 설정 여부 및 사고별 자기부담금은 보험증권 기준으로 적용합니다.']
  cond.append('가해자 상대 소송 제기·수행을 위한 실제 변호사·소송비용을 보상하며 소송 상대방 부담액은 제외합니다.' if i==4 else '정신건강의학과 전문의의 진료·치료 및 그 처방에 따른 해당 기관 내 심리치료사 치료비를 보상합니다. 전문의 처방 없이 심리상담센터 등에서 받은 치료비는 제외합니다. 한도공유 할인 미적용 시 담보가입금액의 40%, 적용 시 총보상한도액 ÷ 가입 담보 수 × 40% 한도입니다.')
 if i in [22,29,33,35]:cond.append('사망담보는 15세 미만 가입 불가입니다.')
 if i in [50,51]:cond.append('여행 중 발생한 질병의 직접 원인으로 보험기간 마지막 날부터 30일 이내 지급사유가 발생한 경우도 보상합니다. 질병사망의 보험만기는 80세 이하이며 개인당 보험금액 2억원 한도입니다.')
 if i in [46,66,67]:cond.append('기존 담보의 위험·면책 범위 확장이며 별도 추가 가입금액 지급으로 합산하지 않습니다.')
 if i>=73:
  cond=['국내여행 중 발생한 해당 상해·질병의 치료 목적 의료비에 한하여 이 행의 보장종목 및 치료별 기준을 적용합니다. 실제 본인부담액에서 약정 자기부담금을 공제하고 중복 실손계약은 비례분담합니다. 국민건강보험·의료급여 미적용 시 약관상 40% 지급기준을 적용하고, 의료비 감면 시 감면 후 실제 부담액을 기준으로 합니다. 미용·성형, 건강검진·예방 목적, 임신·출산 등 약관상 보상 제외 의료비는 지급하지 않습니다. 예외적으로 보상하는 치료 및 상해·질병별 제외 기준은 해당 보장종목 약관을 적용합니다.']
  if i in [73,74]:cond.append('국민건강보험 미가입자 추가특약에 가입한 경우 기본형 실손의료비를 건강보험 가입자와 동일 기준으로 적용합니다. 자동차보험·산재보험에서 보상받지 못한 본인부담의료비는 기본형 해당 조항 기준으로 보상합니다.')
  if i in [75,76]:cond.append('3대비급여는 이 담보에서 제외하며 별도 가입 담보로 보상합니다. 비급여 통원은 연간 100회 한도입니다.')
  if i==77:cond.append('연간 상해·질병 치료행위 합산 50회, 최초 10회 보장 후 객관적 검사로 증상 개선·병변 호전 등을 확인한 경우 10회 단위로 보상합니다.')
  if i==78:cond.append('치료 목적이며 약관상 허가·신고된 효능·효과에 따라 사용하는 주사료에 한하여 연간 상해·질병 치료행위 합산 50회 보상합니다.')
 if i==49:cond.append('식중독 진단확정 후 직접 치료 목적으로 4일 이상 계속입원해야 하며 4일째부터 1회 입원당 120일 한도입니다.')
 out.append({**x,'coverage_target':clean(target),'coverage_amount':amount,'coverage_conditions':' '.join(dict.fromkeys(cond)),'updated_at':now})
(p/'revised.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print('rows',len(out),'conditions average',round(statistics.mean(len(x['coverage_conditions']) for x in r)),round(statistics.mean(len(x['coverage_conditions']) for x in out)))
print('long',[(x['id'],len(x['coverage_target']),len(x['coverage_conditions'])) for x in out if len(x['coverage_target'])>1300 or len(x['coverage_conditions'])>5000])
