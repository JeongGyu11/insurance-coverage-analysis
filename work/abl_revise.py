import json,re,shutil,statistics
from pathlib import Path
from datetime import datetime,timezone,timedelta
p=Path('work/abl_revision');p.mkdir(exist_ok=True)
original=Path('outputs/ABL생명_2507_담보분석.xlsx')
if not (p/'original.xlsx').exists():shutil.copy2(original,p/'original.xlsx')
r=json.loads(Path('work/records.json').read_text(encoding='utf8'));plans=json.loads(Path('work/table_plan.json').read_text(encoding='utf8'));pages=[json.loads(Path(f'work/fast/p{i}.json').read_text(encoding='utf8')) for i in range(4)]
now=datetime.now(timezone(timedelta(hours=9))).isoformat(sep=' ',timespec='seconds')
def compact(x):return re.sub(r'\s+','',x or '').replace('\x00','')
def clean(x):
 x=re.sub(r'\s+',' ',x or '').replace('\x00','').strip()
 repairs={'중 증':'중증','경도치 매':'경도치매','중등도치 매':'중등도치매','증등도치매':'중등도치매','연 금':'연금','보험 료':'보험료','보장개시 일':'보장개시일','보험계약 해당일':'보험계약해당일','보험가입금 액':'보험가입금액','진단 확정':'진단확정','직 접':'직접','수 술':'수술','지 급':'지급','최 초':'최초','피보험 자':'피보험자','재 해':'재해','고 의':'고의'}
 for a,b in repairs.items():x=x.replace(a,b)
 for term in ['중증갑상선암','중등도치매','경도치매','표적항암약물허가치료','기타피부암','제자리암','최초','보장개시일','직접적인','보험료','피보험자','입원일수','사용일수','요양병원','중증치매','뇌손상']:
  x=re.sub(r'\s*'.join(map(re.escape,term)),term,x)
 x=x.replace('증등도 치매','중등도치매')
 x=re.sub(r'제\s*\d+항(?:\s*내지\s*제\s*\d+항)?에서 정한\s*','',x)
 x=re.sub(r'\b에 따라\s*','',x)
 return x
def concise(x):
 x=clean(x);x=re.sub(r'제\s*\d+조(?:의\d+)?\s*[\(［\[][^)］\]]*[)］\]]','',x)
 x=re.sub(r'\(이하[^)]{0,100}\)','',x);x=re.sub(r'\[?\(?별표\s*\d+[^)\]]{0,50}[)\]]','약관 분류표',x)
 x=re.sub(r'[①-⑳]','',x);x=re.sub(r'\s+',' ',x)
 return x.strip(' ;.：:')
def scope(x):
 t=compact(x['target']);name=compact(x['name']);cause=compact(x['cause'])
 if '본인형' in t and '배우자형' in t:return '본인형은 주계약 피보험자, 배우자형은 주계약 피보험자의 가족관계등록부상 배우자'
 if '종피보험자' in name:return '부부계약의 종피보험자(주피보험자의 가족관계등록부상 배우자)'
 if '주피보험자' in name:return '부부계약의 주피보험자'
 if '개인계약' in t and '부부계약' in t:return '개인계약의 피보험자 또는 선택한 부부계약의 주·종피보험자(법률상 배우자)'
 if '전환전' in t:return '전환 전 계약의 피보험자(복수 피보험자 계약은 계약자가 선택한 1명; 계약 소멸에 준하는 전환은 전환 전 보험수익자)'
 if '연금개시전' in t and '연금개시후' in t:return '전환 전 계약 피보험자 또는 연금개시 후 계약에서 정한 피보험자'
 return '여성 피보험자' if '여성피보험자' in t else '해당 계약의 피보험자'
def relevant(text,x):
 t=compact(text);name=compact(x['name']);cause=compact(x['cause'])
 if ('납입면제' in t or re.search(r'보험료.{0,25}납입.{0,15}면제|보험료.{0,20}면제|면제된|면제한',t)) and '납입면제' not in name:return False
 if '계약자적립액' in t and '사망' in t and not any(z in name for z in ['사망','연금','생활자금','노후설계']):return False
 if '갱신' in t and '갱신형' not in compact(x['section']):return False
 if '대장점막내암' in t and '제자리암' in t and not any(z in name for z in ['대장점막','제자리','암진단','암직접']):return False
 if '중증갑상선암진단급여금을더하여' in t and '갑상선암' not in name:return False
 if '재진단' in t and '재진단' not in name:return False
 if '치매' in name and '중증' in name and ('경도치매' in t or '중등도치매' in t) and '중증치매' not in t:return False
 if ('종신연금형' in name and '보증금액부' in name) and '보증기간부' in t:return False
 if '90일' in t and '보장개시' in t:
  if '암보장개시' not in cause and '중증갑상선암' not in name and '납입면제' not in name:return False
  if '치매' in t and '치매' not in name:return False
 if any(z in t for z in ['종신연금','상속연금','확정연금','보증지급기간','노후설계자금']):
  if '상속연금' in name and ('종신연금' in t or '확정연금' in t):return False
  if '확정연금' in name and ('종신연금' in t or '상속연금' in t):return False
  if '종피보험자' in name and '확정연금형' in t:return False
  if '노후설계자금' in t and '노후설계자금' not in name and x['doc']==0 and x.get('table_start')!=55:return False
 return True
def splitnotes(x):
 text=x['conditions'];text=text.split('보험금 지급 제외:')[0].split('보장범위 제외:')[0]
 # The original payment-table extractor stopped at the last benefit cell,
 # although numbered notes often continue on the following PDF page.
 if x['doc']!=0:
  start=x.get('table_start')
  if start:
   body='\n'.join(pages[x['doc']][start-1:start+12])
   m=re.search(r'\(주\)\s*1\.',body)
   if m:
    extra=body[m.start():]
    extra=re.split(r'\(별표\s*[2-9]\)|\(별표\s*1\)|무배당[^\n]{0,100}특약',extra)[0]
    text=extra
    offset=m.start()+len(extra)
    used=0
    for n,s in enumerate(pages[x['doc']][start-1:start+12]):
     used+=len(s)+1
     if used>=offset:x['notes_page_end']=start+n;break
 if text.startswith(x['cause']):text=text[len(x['cause']):]
 text=re.sub(r'^\s*\(주\)\s*','',text)
 blocks=re.split(r'(?<!\d)(?:^|\s)(\d{1,2})\.(?!\d)\s*',text);out=[]
 if blocks[0].strip():out.append(blocks[0])
 out.extend(blocks[i+1] for i in range(1,len(blocks)-1,2))
 return [b for b in out if b.strip()]
def format_amount(x):
 text=clean(x['amount']);text=re.sub(r'\s*[；;]\s*','; ',text)
 # Some original cells repeat their payment event before the actual money.
 for cause in re.split(r'\n',x['cause']):
  c=clean(cause)
  if len(c)>30 and text.startswith(c):text=text[len(c):].lstrip('：: ;')
 text=re.sub(r'피보험자가[^：:;]{20,900}(?:때|경우)(?:\([^)]*\))?[：:]','',text)
 basis=clean(x['basis']);intro=('지급통화는 미국 달러(USD)입니다. ' if '미국 달러' in basis else f'{basis} 기준 지급액입니다. ' if basis else '')
 if '납입면제' in compact(x['name']):return '약관상 납입면제 대상계약과 해당 특약의 차회 이후 보험료 납입을 면제합니다. 현금 보험금 지급은 아닙니다.'
 if '연금' in compact(x['name']) and '산출방법서' in text:intro+='연금액은 계약자적립액·전환일시금과 약정 이율·연금사망률 등에 따라 산출되며 고정 원화액이 아닙니다. '
 text=text.replace('경과기간','계약 경과기간').replace('：',': ')
 if not text.endswith(('.','다.')):text+='을 지급합니다.' if re.fullmatch(r'[\d,.]+만원',text) else ' (약관상 지급기준).'
 if re.fullmatch(r'[\d,.]+만원',clean(x['amount'])) and '보험가입금액' in basis:
  a=re.search(r'([\d,]+)만원',x['amount']);b=re.search(r'([\d,]+)만원',basis)
  if a and b:
   ratio=int(a[1].replace(',',''))/int(b[1].replace(',',''))*100
   text=text.rstrip('.')+f' (특약보험가입금액의 {ratio:g}%).'
 if '보험가입금액' in basis:intro+='공시 지급표의 기준가입금액이며 실제 지급액은 가입한 금액을 적용합니다. '
 return intro+text
out=[];audit=[]
for x in r:
 if not x['cause'].strip():
  prev=next(a for a in reversed(r[:x['id']-1]) if a['doc']==x['doc'] and a['table_start']==x['table_start'] and a['cause'].strip())
  x={**x,'cause':prev['cause']}
 name=compact(x['name']);cause=concise(x['cause']);basis=compact(x['basis'])
 event=re.sub(r'\(다만.*\)\s*$','',cause);event=re.sub(r'\([^)]*(?:최초|한도|연간|1회당)[^)]*\)','',event)
 event=event.split('용어해설')[0]
 event=re.sub(r'(되었을 때|되었을때|받았을 때|받았을때|하였을 때|하였을때|있을 때|있을때)\s*$',lambda m:{'되었을때':'된 경우','받았을때':'받은 경우','하였을때':'한 경우','있을때':'있는 경우'}[m.group().replace(' ','')],event)
 event=re.sub(r'\s*(?:의|이|에서)?\s*지급주기 지급시기 및 지급기간.*','',event)
 person=scope(x);prefix=person+'입니다.' if person.startswith('본인형') else '보장대상은 '+person+'입니다.'
 target=prefix+' '+event.rstrip('.')+(' 보장합니다.' if event.rstrip().endswith('경우') else '에 해당하는 경우를 보장합니다.')
 conditions=[]
 if x['section'].startswith('무배당 ABL'):conditions.append('보험기간 중 해당 지급사유가 발생한 경우 적용합니다.')
 else:conditions.append('해당 특약을 가입한 계약에 적용합니다.')
 for limit in re.findall(r'\([^)]*(?:최초|한도|연간|1회당|일당|개월|년간|동안)[^)]*\)',x['cause']+' '+x['amount']):conditions.append(concise(limit).strip('()'))
 if '부목' in x['cause']:conditions.append('부목(Splint Cast) 치료는 제외합니다.')
 # Retain all specifically quantified waiting periods, repetitions, deductions and exceptions from relevant numbered notes.
 for block in splitnotes(x):
  if not relevant(block,x):continue
  b=concise(block)
  if not b or len(b)<8:continue
  if not any(z in compact(b) for z in ['최초','한도','보장개시','지급','차감','제외','보장하지','진단','입원','통원','보증','동일','확정','선택','인출','취소','최저','환급']):continue
  if b and b not in cause and b not in x['amount']:conditions.append(b)
 # Underwriting age, death reserve and premium-waiver administration are not repeated in unrelated cash benefits.
 filtered=[]
 for c in conditions:
  if not relevant(c,x):continue
  c=re.sub(r'설명\s.*','',c).strip()
  if c and compact(c) not in {compact(a) for a in filtered}:filtered.append(c)
 if '암보장개시' in compact(x['cause']) and not any('90일' in compact(c) for c in filtered):
  plan=next((q for q in plans if q['doc']==x['doc'] and q['start']==x.get('table_start')),None)
  if plan:
   body=' '.join(pages[x['doc']][plan['section_start']-1:plan['start']-1]);body=clean(body)
   if re.search(r'암\s*보장개시일[^。]{0,180}?90일',body):filtered.append('암 보장개시일은 최초계약일(부활 시 부활일)을 포함해 90일이 지난 날의 다음 날입니다. 갱신계약의 보장개시는 해당 특약 조항을 적용합니다.')
 if '보험금 지급 제외:' in x['conditions'] and '사망' in name:
  filtered.append('고의 자해·보험수익자 또는 계약자의 고의 가해는 제외합니다. 심신상실 상태의 자해와 보장개시 후 2년 경과 자살 등은 해당 사망담보의 예외 규정을 적용합니다.' if '2년' in x['conditions'] else '고의 자해·보험수익자 또는 계약자의 고의 가해는 제외하며, 심신상실 등 해당 담보에서 정한 예외를 적용합니다.')
 if '납입면제' in name:filtered=[concise(x['cause'])]+[concise(b) for b in splitnotes(x) if relevant(b,x) and '면제' in b]
 if x['doc']==0 and any(z in name for z in ['종신연금','생존연금','확정연금','상속연금','노후설계자금']):
  filtered=['계약에서 선택한 연금형태와 지급주기를 적용합니다. 연금액은 공시이율 변동과 계약관리비용 차감에 따라 달라집니다.']
  if '보증기간부' in name or ('생존연금' in name and '주피보험자' in name):filtered.append('선택한 보증지급기간 중 사망해도 잔여 보증연금을 지급하며, 약관상 할인 계산한 일시금 수령이 가능합니다.')
  if '보증금액부' in name:filtered.append('연금개시 후 사망 시 이미 지급한 연금총액이 연금개시 시점의 적립액보다 적으면 차액을 일시금으로 지급합니다.')
  if '확정연금' in name:filtered.append('선택한 확정지급기간 중 사망해도 미지급 연금을 약정 횟수까지 지급합니다.')
  if '상속연금' in name:filtered.append('적립액 인출 시 인출금액·수수료와 해당 이자를 차감하여 연금액을 계산합니다.')
  if '종피보험자' in name:filtered.append('주피보험자 사망 후 보증지급기간이 경과한 다음 보험계약해당일부터 종피보험자가 생존한 경우 지급합니다.')
  if '노후설계자금' in name:filtered.append('노후설계자금 선택비율과 지급시기에 따라 지급하며, 연금액은 해당 선택금액을 반영해 산출합니다.')
  if all(z in compact(x['conditions']) for z in ['1.25%','1.0%','0.5%']):filtered.append('최저보증이율은 경과기간 5년 이하 연복리 1.25%, 5년 초과 10년 이하 1.0%, 10년 초과 0.5%입니다.'+(' 전환특약은 전환 전 계약기간을 합산합니다.' if '전환전계약' in compact(x['conditions']) else ''))
 if x['id']==2:
  target='해당 계약의 피보험자에 대한 연금개시 전 생활자금입니다. 계약에서 선택한 지급주기와 이율확정기간 동안 지급합니다.'
  filtered=['매월 지급은 계약일부터 1개월 경과 후부터 5년형 60개월·10년형 120개월, 매년 지급은 계약일부터 1년 경과 후부터 5년형 5년·10년형 10년 동안 지급합니다.']
 if '납입면제' in name:
  target=prefix+' '+concise(x['cause'].split('용어해설')[0].split('(다만')[0])
  filtered=['해당 납입면제 특약에 가입하고 약관상 면제사유를 충족한 경우 적용합니다.']
  if '암' in name:
   filtered.append('암은 최초계약일(부활 시 부활일)부터 그 날을 포함하여 90일이 지난 다음 날부터 보장합니다. 중증 이외의 갑상선암·기타피부암·대장점막내암은 제외합니다.')
   if '갱신' in compact(x['section']):filtered.append('갱신계약의 암 보장개시는 갱신일입니다. 면제 대상계약이 갱신되면 갱신 보험료는 납입해야 합니다.')
  else:
   filtered.append(concise(x['cause'].split('용어해설')[0]))
  if '고의' in x['conditions']:filtered.append('고의 가해 등 약관상 납입면제 제외사유는 적용하지 않으며, 심신상실 등 예외는 해당 조항을 따릅니다.')
 if x['doc']==0 and '장기요양연금' in name:
  filtered=['약관상 장기요양상태 진단확정 후 매년 계약해당일에 생존해야 지급합니다. 선택한 10년 또는 20년의 한도기간은 생존연금 보증지급기간을 넘을 수 없습니다. 장기요양 재판정 결과가 보장등급에 해당하지 않으면 지급을 중지하고, 다시 해당되면 남은 연금을 지급합니다. 연금액은 공시이율과 계약관리비용 차감을 반영합니다.']
 if name in ['최초1회치료비','연간1회치료비'] and '계속받는표적항암' in compact(x['section']):
  filtered=['최초 치료 시 최초 1회 치료비와 연간 1회 치료비를 함께 지급합니다. 최초 치료비는 1회 한도이며, 연간 치료비는 계약일 기준 매 1년 기간마다 1회 한도입니다. 최초계약은 90일 경과 다음 날부터 암을 보장하며, 부활 시 다시 90일을 적용하고 갱신 시에는 갱신일부터 보장합니다. 갱신계약에는 1년 미만 감액을 적용하지 않습니다. 식약처 허가 효능·효과 내 사용 또는 암질환심의위원회 심의 후 심평원이 승인한 해당 요양기관의 요법에 한해 보장합니다.']
 if '치매진단급여금' in name:
  filtered=['해당 특약 가입 및 약관상 치매상태의 최종진단확정 시 최초 1회에 한해 지급합니다.']
  if '중증' not in name:filtered.append('경도·중등도치매는 계약일(부활일)부터 1년 경과 다음 날부터 보장합니다. 재해로 인한 뇌손상이 직접 원인인 경우는 계약일(부활일)부터 보장합니다. 보장개시 전 해당 상태가 발생·확정되면 이후 재진단해도 해당 급여금을 지급하지 않습니다.')
  if '경도' in name:filtered.append('중등도·중증치매 급여금을 이미 받은 경우 경도치매 급여금을 추가 지급하지 않습니다.')
  elif '중등도' in name:filtered.append('이미 받은 경도치매 급여금은 차감하며, 중증치매 급여금 지급 후에는 중등도치매 급여금을 추가 지급하지 않습니다.')
  else:filtered.append('이미 지급한 경도·중등도치매 급여금 합계는 차감합니다.')
 if name=='암진단급여금' and '보장범위 제외:' in x['conditions']:
  definition=compact(x['conditions'].split('보장범위 제외:')[1].split('보험금 지급 제외:')[0])
  if '중증갑상선암' in definition and '포함' in definition:filtered.append('암의 범위는 약관 분류표에 따르며 중증 이외의 갑상선암·기타피부암·대장점막내암·전암상태는 제외합니다. 중증갑상선암은 암에 포함합니다.')
  elif 'C73' in definition and 'C44' in definition:filtered.append('약관상 암 분류표를 적용하며 갑상선암·기타피부암·전암상태는 암 담보에서 제외합니다.')
 short=[]
 for c in filtered:
  t=compact(c)
  if '보장개시일' in t and '암' in t and '90일' in t and not any(z in t for z in ['2년','1년','차감','제외','치료비','6대질병','중증질환','동시에']):
   c=('중증갑상선암' if '중증갑상선암' in t else '암')+' 보장개시는 최초계약일(부활 시 부활일)부터 그 날을 포함하여 90일 경과 다음 날입니다.'+(' 갱신계약은 갱신일부터 보장합니다.' if '갱신일' in t else '')
  elif '연간' in t and '매1년' in t and '의미' in t:c='연간 한도는 계약일부터 매 1년 단위의 계약해당일 전일까지를 기준으로 계산합니다.'
  elif all(z in t for z in ['입원일수','1년','50%','100%']):c='입원이 계약 1년 경과 시점을 넘겨 계속되면 1년 미만 입원일은 50%, 1년 이후 입원일은 100%를 지급합니다.'
  elif all(z in t for z in ['중증갑상선암','더하여지급','이미지급']):c='중증갑상선암 급여금 지급 시 갑상선암(초기제외) 급여금을 추가 지급합니다. 다만, 해당 급여금을 이미 받아 세부보장이 소멸한 경우는 추가 지급하지 않습니다.'
  if c not in short:short.append(c)
 filtered=short
 amount=format_amount(x);new={**x,'target':clean(target),'amount_display':amount,'conditions_display':' '.join(c.rstrip('.')+'.' for c in filtered),'updated_at':now}
 if name in ['최초1회치료비','연간1회치료비'] and '계속받는표적항암' in compact(x['section']):
  vals=re.findall(r'[\d,]+만원',x['amount'])
  if len(vals)==2:new['amount_display']=clean(x['basis'])+' 기준, 최초계약 경과기간 1년 미만 '+vals[0]+', 1년 이상 '+vals[1]+'을 지급합니다. '+('최초 치료 시 1회 지급합니다.' if name=='최초1회치료비' else '치료가 발생한 연간 기간에 1회 지급합니다.')
 if not new['conditions_display']:new['conditions_display']='해당 특약 가입 및 보험기간 중 담보별 지급요건 충족 시 적용합니다.'
 out.append(new)
 if len(new['conditions_display'])>1500 or len(new['target'])>900 or len(amount)>1600:audit.append({'id':x['id'],'name':x['name'],'condition_chars':len(new['conditions_display']),'amount_chars':len(amount),'target_chars':len(new['target'])})
(p/'revised.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');(p/'audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf8')
print('rows',len(out),'review',len(audit),'conditions average before/after',round(statistics.mean(len(x['conditions']) for x in r)),round(statistics.mean(len(x['conditions_display']) for x in out)))
print(json.dumps(audit[:15],ensure_ascii=False))
