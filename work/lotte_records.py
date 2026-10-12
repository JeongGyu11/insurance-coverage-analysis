from pathlib import Path
import json,re
from datetime import datetime,timezone,timedelta
p=Path('work/lotte');m=json.loads((p/'manifest.json').read_text(encoding='utf8'));ss=json.loads((p/'sections.json').read_text(encoding='utf8'));r=[];excluded=[]
now=datetime.now(timezone(timedelta(hours=9))).isoformat(sep=' ',timespec='seconds')
def clean(t):return re.sub(r'\s+',' ',t or '').strip()
def compact(t):return re.sub(r'\s+','',t or '')
def pages(k):return json.loads((p/(k+'_clean.json')).read_text(encoding='utf8'))
def section(k,n):return next(s for s in ss[k] if s['start']==n)
def cond(s):
 selected=[]
 for a in s['articles']:
  title=a['title']
  if any(z in title for z in ['보상하는 손해','지급사유','지급하는 사유','보상하지','지급하지','세부규정','정의','보상한도','지급한도','보험금의 지급','보험가입금액','보험목적','보험 목적','손해액의 조사','손해액의 평가','손해방지','적용범위','적용 범위','운동경기의 종목','보험금의 분담','보험금의 비례분담','의무보험과의 관계','손해배상청구에 대한 회사의 해결']):
   if any(z in title for z in ['통지','절차','청구','설명 의무','발생의','발생통지']):continue
   text=a['text'];text=re.split(r'(?m)^【별표\s*\d+】',text)[0];selected.append(clean(text))
 return '\n'.join(dict.fromkeys(selected))
def add(k,s,name,amount,target=None,review='',extra='',source_page=None,condition=None):
 f=next(x for x in m if x['key']==k);q=next(x for x in m if x['kind']=='상품요약서' and x['product_folder']==f['product_folder']);b=next(x for x in m if x['kind']=='사업방법서' and x['product_folder']==f['product_folder']);product='let:guard 안심사이버보험' if k=='doc2' else 'let:discover 국내여행보험Ⅱ'
 common=ss[k][0];commoncond='\n'.join(clean(a['text']) for a in common['articles'] if a['title'] in ['보상하지 않는 손해','보험금을 지급하지 않는 사유','보험금 등의 지급한도','보험금의 비례분담'])
 if condition is None:condition=cond(s)
 if s['start']!=common['start']:condition+='\n[보통약관 공통 사항: 특별약관에서 정한 적용·변경·제외 기준 우선]\n'+commoncond
 if k=='doc2':condition+='\n특별약관은 가입한 담보만 적용. 총보상한도액 설정 시 여러 담보 지급액의 합계는 총한도 내에서 보상하며, 1사고에 여러 담보 적용 시 가장 큰 자기부담금 적용. 총한도 미설정 시 담보별 자기부담금 적용. 보험료 예시의 가입금액·자기부담금을 실제 계약조건으로 확정하지 않음.'
 else:condition+='\n특별약관은 보험증권에 명기된 가입특약만 적용. 국내여행 중 피보험자·보험목적·피해자 범위와 적용 담보별 면책사항은 해당 조항 기준.'
 if extra:condition+='\n'+extra
 target=target or ('피보험자(대한민국 내 보험기간 중 발생한 해당 손해·상해; 금융사기 가입은 만 10세 이상)' if '금융사기' in name else '피보험자(보험증권상 보장지역·보험기간 및 해당 담보 적용범위)' if k=='doc2' else '보험증권에 기재된 국내여행 중 피보험자(주거지·반려동물·배상책임 담보는 별도 보험목적·피해자 범위 적용)')
 r.append(dict(id=len(r)+1,company_name='롯데손해보험',product_name=product,coverage_name=name,coverage_target=target,coverage_amount=amount,coverage_conditions=condition.strip(),created_at=now,updated_at=now,source_file=f['path'],source_page=source_page or f"{s['start']}–{s['end']}",source_name=s['name'],summary_file=q['path'],summary_page='1–4' if k=='doc2' else '3–5',business_file=b['path'],review=review or '사업방법서·상품요약서·약관 대조. 선택특약은 실제 가입 시 적용.',type='기본계약' if s['name']=='보통약관' else '선택계약'))
face='보험증권에 기재된 해당 담보 보험가입금액(사고별 지급단위 및 중복 제한은 보장조건 참조)'
loss='실제 부담한 보상대상 손해·비용에서 약정 자기부담금 및 환급·회수·보상금 등을 공제한 금액; 보험증권의 담보별 보상한도 내(비례분담·총한도는 약관 및 계약 기준)'
for k in ['doc2','doc5']:
 for s in ss[k]:
  n=s['start'];title=s['name'];pay=next((a for a in s['articles'] if a['title'] in ['보험금의 지급사유','보상하는 손해','보험금을 지급하는 사유']),None)
  if k=='doc2' and n==21:excluded.append([k,n,title,'별도 기본담보 없음; 선택특약의 보상·공통 한도 규정']);continue
  if k=='doc5' and n==27:
   add(k,s,'국내여행 중 상해사망','보험증권의 사망보험가입금액 전액',extra='사망담보: 15세 미만 가입 불가; 그 밖의 가입 제한은 약관·사업방법서 기준.')
   add(k,s,'국내여행 중 상해후유장해','보험증권의 후유장해보험가입금액 × 장해분류표의 해당 장해지급률(동일 사고 합산한도는 가입금액)');continue
  if k=='doc5' and n in [61,62]:excluded.append([k,n,title,'기존 보장의 지급범위 제한 또는 부담보 제도; 별도 지급담보 아님']);continue
  if '실손의료비' in title:continue
  if not pay:excluded.append([k,n,title,'가입·정산·보험수익자·환율·청구 등 운영 제도; 독립 지급담보 없음']);continue
  name=compact(re.sub(r'\s*(?:추가보장\s*)?특별약관','',title));amount=face;extra='';review=''
  if '보상하는 손해'==pay['title']:amount=loss
  if '부재'==name:amount='주거지 도난손해 담보의 보험가입금액·보상한도 및 약관상 손해 산정기준';extra='주거지 도난손해의 72시간 이상 계속 부재 면책을 완화하는 확장특약으로 별도 추가 보상한도가 생기는 것은 아님.'
  if '운동위험' in name:amount='보통약관 및 부가된 특별약관의 담보별 보험가입금액·지급기준';extra='해당 운동위험으로 발생한 기존 상해담보 손해를 확장 보장하는 특약. 추가 가입금액 지급으로 합산하지 않음.'
  if k=='doc2' and n in [50,53]:
   names=['개인정보·신용도용(직접적인 금전적 손실)','개인정보·신용도용(법률비용)'] if n==50 else ['사이버폭력·스토킹(법률비용)','사이버폭력·스토킹(심리상담 및 치료비용)']
   for name in names:
    amount=loss
    if '심리상담' in name:amount='실제 부담한 약관상 심리상담·치료비에서 약정 공제 후 보상. 한도공유 할인 미적용: 사이버폭력·스토킹 가입금액 × 40%; 적용: 총보상한도액 ÷ 가입 담보 수 × 40%'
    add(k,s,name,amount)
   continue
  if k=='doc2' and n==78:amount='보험가입금액 × 부상급수별 지급률: 1급 100%, 2급 60%, 3급 40%, 4급 30%, 5급 16%, 6급 8%, 7급 4%, 8·9·10급 각 2%'
  if k=='doc5' and n in [72,77,79]:
   prefix={72:'교통상해',77:'강도상해',79:'스포츠단체상해'}[n]
   for benefit in ['사망','후유장해']:add(k,s,prefix+benefit,'보험증권의 사망보험가입금액 전액' if benefit=='사망' else '보험증권의 후유장해보험가입금액 × 장해분류표의 해당 지급률',extra='해당 특약의 위험 범위 및 보통약관의 지급기준을 적용.')
   continue
  if k=='doc5' and n==115:
   for benefit in ['질병사망','질병80%이상고도후유장해']:add(k,s,benefit,'해당 특약의 사망보험가입금액 전액',extra='사업방법서상 질병사망 보험만기 80세 이하, 보험금액 개인당 2억원 한도. 여행 중 발생한 질병의 직접원인으로 보험기간 마지막 날부터 30일 이내 지급사유 발생도 보상.')
   continue
  if k=='doc5' and n in [89,90]:amount='장해지급률 100%: 보험가입금액 100%; 80% 이상 100% 미만: 70%; 50% 이상 80% 미만: 35%; 일시금 지급(분할 요청 시 약관 이율·기준 적용)'
  if k=='doc5' and n==108:amount='보험증권의 입원일당 가입금액 × 지급대상 입원일수(1회 입원당 180일 한도)'
  if k=='doc5' and n==113:amount='보험증권의 식중독 입원일당 가입금액 × 4일째부터 지급대상 입원일수; 1회 입원당 120일 한도';review='요약서의 입원일당 일반 안내 180일과 달리 해당 특약은 4일째부터·120일 한도이므로 개별 약관 우선.'
  if k=='doc5' and n==195:amount='확정판결에 의한 대물 벌금 실액; 1사고당 500만원 한도'
  if k=='doc5' and n==197:amount='확정판결에 의한 대인 벌금 실액; 1사고당 2,000만원 한도. 특정범죄 가중처벌법 제5조의13 제2호 적용 벌금: 3,000만원 한도'
  if k=='doc5' and n in [200,204]:amount='실제 지급한 형사합의금. 사망·일반교통사고 중상해: 피해자 1인당 보험가입금액 한도. 중대법규위반 42~69일: 1천만원; 70~139일: 가입금액 3천/5천/7천/1억원별 2천/3천/4천/5천만원; 140일 이상: 가입금액 한도'
  if k=='doc5' and n in [208,212]:amount='실제 지급한 형사합의금; 피해자 1인당 사망·일반교통사고 중상해 3천만원 한도; 중대법규위반 42~69일 1천만원, 70~139일 2천만원, 140일 이상 3천만원 한도'
  if k=='doc5' and n==216:amount='실제 지급한 형사합의금; 사고마다 피해자 각각 500만원 한도';extra='동승자포함 또는 동승자제외 교통사고처리지원금 특약 중 하나 이상 가입 및 유효한 계약에 한하여 적용.'
  if k=='doc5' and n==220:amount='실제 부담한 약관상 변호사선임비용; 1사고마다 해당 보험가입금액 한도'
  if k=='doc5' and n==232:amount='일일 보험가입금액 × 약관상 억류 기간(관할기관 신고 시점부터 구출·해제·사망 확인 시점까지); 90일 한도'
  if k=='doc5' and n==259:amount='보험증권에 기재된 해당 담보 보험가입금액; 원인·종류·부위와 관계없이 연간 1회 한도'
  if k=='doc5' and n==273:amount='제주 출발 항공편 결항으로 최초 출발예정시각부터 24시간 내 추가로 발생한 식음료비·교통비·숙박비의 실제 부담액; 보험가입금액 한도, 최초 1회'
  if k=='doc5' and n==245:
   add(k,s,'반려동물(맹견제외)배상책임(대인·대동물)','손해배상금: 자기부담금 초과액을 사고별 보상한도 내 지급. 소송·변호사·중재·화해·조정비용 및 공탁보증보험료: 손해배상 보상액과 합산한도 내. 약관상 손해방지·구상권 보전·회사 요청 비용: 전액. 보험기간 총 보상한도 적용.',target='보험증권상 반려동물(맹견 제외)의 행위로 신체장해를 입은 타인 및 손해를 입은 타인 소유 반려동물',extra='타인 재물 일반 손해까지 자동 확대하지 않음. 손해배상금과 약관상 소송·손해방지비용 범위 적용.');continue
  if k=='doc5' and n==233:
   add(k,s,'국내여행 중 배상책임','손해배상금: 약정 자기부담금 초과액을 보험증권의 보상한도 내 지급. 소송·변호사·중재·화해·조정비용 및 공탁보증보험료: 손해배상 보상액과 합산한도 내. 약관상 손해방지·구상권 보전·회사 요청 비용: 전액.',target='국내여행 중 우연한 사고로 신체장해 또는 재물 손해를 입은 타인; 피보험자의 법률상 배상책임',extra='보험증권상 자기부담금 공제. 손해배상금과 약관상 소송·손해방지비용은 각각 한도 규정 적용.');continue
  add(k,s,name,amount,extra=extra,review=review)
# The non-driver benefit is described only in the product summary supplied.
s=section('doc2',78)
add('doc2',s,'자동차사고부상(비운전자)(1~10급)','보험가입금액 × 부상등급별 약정 지급비율(비운전자 전용 지급비율표는 제공 자료에서 확인 불가)',target='자동차 운전 중을 제외한 탑승 중·비탑승 중 자동차사고로 부상등급 1~10급을 받은 피보험자',review='확인 필요: 요약서 PDF 3페이지에 기재되지만 약관에는 운전자 담보만 제공. 운전자 비율·면책을 비운전자에 임의 적용하지 않음.',source_page='해당 전용 약관 미제공',condition='상품요약서 PDF 3페이지의 비운전자 담보 지급사유 기준: 운전 중 제외, 탑승 중·비탑승 중 사고의 직접결과로 자동차손해배상보장법 시행령상 부상등급 1~10급을 받은 경우. 상세 지급비율·면책은 비운전자 전용 약관 확인 필요.')
r[-1]['source_file']='';r[-1]['source_name']='자동차사고부상(비운전자)(1~10급): 상품요약서만 확인';r[-1]['summary_page']='3'
# Medical expense benefit types have separate monetary limits and deductibles.
k='doc5';a=pages(k)
for start,names in [(118,['상해급여','질병급여']),(164,['상해비급여','질병비급여','도수치료·체외충격파치료·증식치료','비급여주사료','비급여자기공명영상진단'])]:
 s=section(k,start)
 for name in names:
  if name.endswith('급여') and '비급여' not in name:
   amount='급여 본인부담금 입원 80%; 통원: 실제 보장대상 의료비 − max(20%, 의료기관별 1만원 또는 2만원). 입원·통원 합산 계약별 연간 가입금액(최대 5천만원), 통원 1회 계약별 한도(최대 20만원). 입원 공제금액 연간 200만원 초과분은 약관 한도 내 보상'
   condition='\n'.join(a[118:131]);sp='119–131'
  elif name in ['상해비급여','질병비급여']:
   amount='3대비급여 제외: 입원 비급여 의료비(병실료 제외) 70%; 상급병실료 차액 50%(1일 평균 10만원 한도); 통원 실액 − max(30%, 3만원), 연간 100회. 입원·통원 합산 계약별 연간 가입금액(최대 5천만원), 통원 1회 계약별 한도(최대 20만원)'
   condition='\n'.join(a[164:174]+a[178:186]);sp='165–174, 179–186'
  else:
   limit={'도수치료·체외충격파치료·증식치료':'연간 350만원, 각 상해·질병 치료행위 합산 50회(최초 10회, 이후 객관적 호전 확인 시 10회 단위)','비급여주사료':'연간 250만원, 각 상해·질병 치료행위 합산 50회','비급여자기공명영상진단':'연간 300만원(조영제·판독료 포함)'}[name]
   amount='보장대상 비급여 의료비 실액 − max(30%, 3만원) / 1회; '+limit
   condition='\n'.join(a[173:186]);sp='174–186'
  more='각 행에 명시한 보장종목·세부치료의 보상·면책 기준만 적용하며 동일 약관의 다른 종목 기준은 대조용. 국민건강보험·의료급여 미적용 시 약관상 40% 지급기준 및 감면 후 실제 본인부담금 기준 적용. 실손 담보는 중복계약 비례분담.'
  if start==118:more+='\n국민건강보험 미가입자 추가특약(PDF 296페이지) 부가 시, 국민건강보험법 적용을 받지 않는 피보험자에게 기본형 실손의료비를 국민건강보험 가입자와 동일하게 적용. 자격 취득 시 추가특약 해지 및 통지. 자동차보험·산재보험에서 보상받지 못한 본인부담의료비는 기본형 제3·4조 기준.'
  add(k,s,name+' 실손의료비',amount,condition=condition,source_page=sp,extra=more);r[-1]['summary_page']='4–5'
r.sort(key=lambda x:0 if 'guard' in x['product_name'] else 1)
for i,x in enumerate(r,1):x['id']=i
assert len({(x['product_name'],x['coverage_name']) for x in r})==len(r)
assert all(len(x['coverage_conditions'])<32767 for x in r)
(p/'records.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');(p/'excluded.json').write_text(json.dumps(excluded,ensure_ascii=False,indent=2),encoding='utf8')
print('rows',len(r),'counts',[(n,sum(x['product_name']==n for x in r)) for n in dict.fromkeys(x['product_name'] for x in r)]);print('max conditions',max(len(x['coverage_conditions']) for x in r));print('excluded',len(excluded));print('\n'.join(str(x['id'])+' '+x['coverage_name'] for x in r))
