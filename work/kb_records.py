from pathlib import Path
import json,re
from datetime import datetime,timezone,timedelta
p=Path('work/kb');m=json.loads((p/'manifest.json').read_text(encoding='utf8'));inv=json.loads((p/'inventory.json').read_text(encoding='utf8'));tabs=json.loads((p/'cells.json').read_text(encoding='utf8'));r=[]
now=datetime.now(timezone(timedelta(hours=9))).isoformat(timespec='seconds').replace('T',' ')
def clean(t):return re.sub(r'\s+',' ',re.sub(r'현재【[^】]+】페이지 입니다\.', '',t).replace('\x00',' ')).strip()
def pages(k):return json.loads((p/(k+'.json')).read_text(encoding='utf8'))
def article(k,n,start=100):
 body='\n'.join(pages(k)[start:]);a=re.search(r'(?m)^제\s*'+str(n)+r'조\s*\[',body)
 if not a:return ''
 b=re.search(r'(?m)^제\s*\d+조(?:의\d+)?\s*\[',body[a.end():]);return clean(body[a.start():a.end()+b.start() if b else len(body)])
def add(product,name,amount,cond,key,page,bodypages,notes='',review='',source=None):
 f=next(x for x in m if x['key']==key);path=source or f['path']
 r.append(dict(id=len(r)+1,company_name='KB라이프생명',product_name=product,coverage_name=name,coverage_target='피보험자(가입나이·보험기간·인수한도는 사업방법서 및 계약별 기준)',coverage_amount=amount,coverage_conditions=cond,created_at=now,updated_at=now,source_file=path,source_page=page,article_pages=bodypages,table_notes=notes,review=review,type='주계약',duplicate_paths=f['duplicate_paths']))
for key,n,kind in [('doc2',128,'상해보장형'),('doc3',135,'치매보장형'),('doc4',130,'상해보장형'),('doc5',136,'치매보장형')]:
 partial=key in ['doc4','doc5'];prod='KB 골든라이프 안심보험 무배당'+('(해약환급금 일부지급형)' if partial else '')+'('+kind+')'
 t=next(x for x in tabs if x['key']==key);a=pages(key);notes='\n'.join(a[n-1:n+1] if '치매' in kind else a[n-1:n]);notes=notes[notes.index('(주 1)'):];common=article(key,5)
 review='사업방법서는 4개 형태 공통. 상품요약서는 표준형 상해·치매 폴더에 동일한 파일로 제공됨. 해당 형태의 개별 약관을 기준으로 기록.'
 for name,cause,amount in t['tables'][0]['rows'][1:]:
  name=clean(name);cond=clean(cause)+'\n';amount='[보험가입금액 1,000만원 기준] '+clean(amount)
  if '상해' in kind:
   if '사망' in name:amount+='; 위 보험금과 사망 당시 해약환급금 중 큰 금액 지급'
   cond+=article(key,4)+'\n보험료 납입기간 중 동일한 재해로 장해지급률 합계 50% 이상이면 차회 이후 보험료 납입 면제.\n'+common
  else:
   cond+='치매보장개시일은 계약일(부활일)부터 그 날을 포함하여 1년이 지난날의 다음날. 질병 없는 상태에서 재해에 의한 뇌 손상이 직접 원인이면 약관의 보장개시일 적용.\n'
   cond+='CDR 척도 경도 1점, 중등도 2점, 중증 3점 이상(동등한 국내 인정 검사 포함). 해당 상태가 90일 이상 지속되고 호전 기대가 없어야 하며 전문의 진단 후 90일 경과 이후 회사가 지속 여부를 확인하여 최종 확정. 알코올중독·의사 처방에 의하지 않은 약물투여에 의한 인지장애 제외.\n'
   cond+=clean(notes)+'\n'+common
  add(prod,name,amount,cond,key,n,f'{107 if key=="doc2" else 108 if key=="doc4" else 107 if key=="doc3" else 108}–{114 if key in ["doc3","doc5"] else 111}',clean(notes),review)
a=pages('doc7');notes=clean('\n'.join(a[135:137]));common=article('doc7',5)
base='연금액은 연금개시시점 계약자적립액과 공시이율을 적용해 산출방법서에 따라 계산. 공시이율 변경 시 연금액도 달라짐. 생활설계자금 선택비율은 0~50%. 매월·3개월·6개월 분할 수령 가능. 2가지 이상 연금형 선택 시 구성비율에 따른 연금액 합계 지급. 기본보험료를 5년(60회) 이상 납입하지 않고 종신연금형을 선택하면 확정·상속연금형과 동시 선택 불가.\n'
guarantee='보증형: 보증시점의 기본보험료 계약자적립액이 최저계약자적립액보다 적으면 최저계약자적립액으로 대체. 최저계약자적립액=보증 기준금액(기준 기본보험료)×보증비율. 납입기간 경과 시 100%(10년납은 7년 경과 시); 10년 경과 시 3·5·7·10년납 각각 130%·126%·119%·114%; 연금개시 시 10년 보증비율+(연금개시전 보험기간-10년)×2%. 약정 기본보험료 미완납이면 완납일로 보증시점 조정. 연금개시시점 보증은 실제 연금지급 개시에 한해 적용. 감액·중도인출 시 기준금액 조정.\n'
unguarantee='미보증형: 연금지급개시시점 계약자적립액이 이미 납입한 보험료(인출금액 차감)+1,000원 이하이면 해당 금액으로 함. 보증형의 특정 시점 최저계약자적립액 보증은 적용하지 않음.\n'
life='종신연금형은 20년·100세·기대여명 보증 중 계약 기준 적용. 보증기간 내 사망해도 미지급 연금을 각 지급일에 지급. 100세 보증 횟수는 100세-연금개시나이. 보증기간 잔여 연금의 공시이율 할인 선지급 가능.\n'
for kind in ['미보증형','보증형']:
 prod='KB 세번의 약속 연금보험 무배당('+kind+')';src=next(x['path'] for x in inv if x['kind']=='약관' and '('+kind+')' in x['product_folder']);g=guarantee if kind=='보증형' else unguarantee
 review='보증형·미보증형 약관/사업방법서는 각각 동일 파일(SHA-256 일치). 사업방법서의 별도 보험종목 및 약관의 유형별 보증 조항을 구분 적용. 상품요약서 없음.'
 items=[
 ('고도재해장해급여금','매월 40만원 × 36회(3년); 최초 1회','연금개시전 보험기간 중 동일한 재해로 여러 신체부위 장해지급률 합계 80% 이상. 지급사유 발생일부터 3년간 매월 해당일 지급(해당일 없는 달은 말일).\n'+article('doc7',4)+'\n'+common,'136'),
 ('생존연금(종신연금형)','연금개시시점 계약자적립액 × (1-생활설계자금 선택비율)을 기준으로 계산한 연금액(미선택 시 비율 0%)','연금개시후 매년 보험계약해당일에 생존.\n'+base+life+g,'136–137'),
 ('생활설계자금','연금개시시점 계약자적립액 × 생활설계자금 선택비율에서 계약관리비용을 차감하고 지급 신청일까지 공시이율로 적립한 금액','연금개시일에 생존. 계약자가 선택한 지급 신청일에 지급하며 신청 전 사망하면 사망일을 신청일로 함. 선택비율 0~50%; 미지정 시 0%로 인출 불가. 기본보험료를 5년(60회) 이상 납입하지 않고 종신연금형 선택 시 비율 0%.\n'+g,'136–137'),
 ('생존연금(확정연금형)','연금개시시점 계약자적립액 × (1-생활설계자금 선택비율)을 기준으로 계산한 연금액; 확정기간 5·10·15·20년','연금개시 전 지급형태 변경 선택. 연금개시후 확정기간의 매년 계약해당일 지급. 기간 내 사망해도 미지급 연금을 각 지급일에 지급. 잔여 연금의 공시이율 할인 선지급 가능.\n'+base+g,'136–137'),
 ('생존연금(상속연금형)','연금개시시점 계약자적립액 × (1-생활설계자금 선택비율)을 기준으로 공시이율에 의해 계산한 연금액; 사망 시 잔여 계약자적립액 지급','연금개시 전 지급형태 변경 선택. 연금개시후 매년 계약해당일 생존 시 지급. 사망 시 사망시점 계약자적립액을 연금수익자에게 지급.\n'+base+g,'137')]
 for name,amount,cond,pg in items:add(prod,name,amount,cond,'doc7',pg,'109–114; 123–125; 136–137',notes,review,src)
assert len(r)==24
(p/'records.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')
print('24 rows; product counts',[(x,sum(a['product_name']==x for a in r)) for x in dict.fromkeys(a['product_name'] for a in r)]);print('max condition',max(len(a['coverage_conditions']) for a in r));assert all(len(a['coverage_conditions'])<32767 for a in r)
