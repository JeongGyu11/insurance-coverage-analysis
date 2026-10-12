import json,re,copy
from pathlib import Path
from datetime import datetime,timezone,timedelta
R=Path('work/fubon');M=json.loads((R/'manifest.json').read_text(encoding='utf8'));T=json.loads((R/'tables.json').read_text(encoding='utf8'));P={i:json.loads((R/f'doc{i}.json').read_text(encoding='utf8')) for i in [1,3,5,7,9]};records=[];audit=[]
stamp=datetime.now(timezone(timedelta(hours=9))).isoformat(sep=' ',timespec='seconds')
def clean(s):return re.sub(r'\s+',' ',re.sub(r'[\ue000-\uf8ff]','',s or '')).strip()
def fix(s):
 for a,b in {'직 접':'직접','직접척인':'직접적인','진 단':'진단','확정 되':'확정되','확정 받':'확정받','특 약':'특약','보 장':'보장','수 술':'수술','갑 상선':'갑상선','기 타피부':'기타피부','피부 암':'피부암','대장점막내 암':'대장점막내암','뇌혈관 질환':'뇌혈관질환','또 는':'또는','으 로':'으로','허 혈':'허혈','이 후':'이후','그 날':'그날','한 하':'한하','발 생':'발생','지 급':'지급','재 해':'재해','상 기':'상기','일 미만':'일 미만','원 으로':'원으로','한 함':'한함','계 약':'계약','목적으 로':'목적으로','인 하여':'인하여','의 원':'의원','계속 하여':'계속하여','실 질적으로':'실질적으로','간호·간병통 합':'간호·간병통합','되 고':'되고','에 생존시':'에 생존한 경우','생활 자금':'생활자금','당/해약':'무배당/해약'}.items():s=s.replace(a,b)
 for a,b in {'직접 적인':'직접적인','이후 에':'이후에','받았 을':'받았을','되었 을':'되었을','최 초':'최초','1 회':'1회','계약 일':'계약일','보장개 시일':'보장개시일','심근경 색증':'심근경색증','심근경 경색증':'심근경색증','특약보험 기간':'특약보험기간','상기 금액':'상기금액','금액 의':'금액의','1년 기본보장기간 미만':'1년 미만','보험금 지급사유가 발 생':'보험금 지급사유가 발생'}.items():s=s.replace(a,b)
 return clean(s)
def toc(di):
 lines='\n'.join(P[di][1:4]).replace('\r','').splitlines();o=[]
 for l in lines:
  z=re.match(r'^(\d{1,4})\s+(.+)',l)
  if z:o.append([int(z[1]),clean(z[2])])
  elif o and clean(l) in ['미지급형','무배당','갱신형']:o[-1][1]+=' '+clean(l)
 return o
def section(di,page):
 offset=18 if di==1 else 30 if di==3 else 29
 a=[(n+offset,s) for n,s in toc(di) if n+offset<=page]
 start,title=a[-1];b=[n+offset for n,s in toc(di) if n+offset>start];end=min(b)-1 if b else len(P[di]);return title,start,end
def add(di,name,target,amount,cond,pages,review=''):
 prod=re.sub(r'^판매중__20250701_','',M[di]['product']).replace('_',' ')
 records.append(dict(id=len(records)+1,company_name='푸본현대생명',product_name=prod,coverage_name=name,coverage_target=target,coverage_amount=amount,coverage_conditions=cond,created_at=stamp,updated_at=stamp,source_file=M[di]['path'],source_page=pages,business_file=M[di-1]['path'],business_page='1–'+str(M[di-1]['pages']),review=review or '지급표의 담보명·대상·기준 가입금액과 약관 본문을 대조.'))
def amount_desc(raw,basis):
 raw=fix(raw);main=re.split(r'\(\s*단',raw)[0].strip();b=fix(basis[0]) if basis else ''
 def money(s):
  z=re.search(r'([\d,]+)만(?:(\d+)천)?원',s)
  return int(z[1].replace(',',''))*10000+(int(z[2])*1000 if z[2] else 0) if z else None
 v,den=money(main),money(b)
 rate=f'가입금액의 {v/den*100:g}%' if v is not None and den else '계약별 약정금액'
 unit='매월 ' if main.startswith('매월') else '매년 ' if main.startswith('매년') else '1일당 ' if main.startswith('1일당') else '수술 1회당 ' if '수술 1회당' in main else '통원 1회당 ' if main.startswith('1회당') else ''
 formula='가입금액 × 해당 장해지급률' if '장해지급률' in main else unit+rate
 return f'{formula}. 지급표 {b.replace("(기준 :", "기준:").rstrip(")")}에서 지급액은 {main}입니다. 실제 지급액은 해당 계약의 가입금액으로 계산합니다.'
for di in [3,5]:
 for t in sorted((v for v in T if v['doc']==di),key=lambda v:v['page']):
  title,start,end=section(di,t['page']);body=fix(' '.join(P[di][start-1:end]));notes=fix(t['notes']);rider=title
  rows=t['rows'];audit.append(dict(doc=di,section=title,start=start,end=end,table=t['page'],rows=len(rows)))
  for ri,row in enumerate(rows):
   if row['name'].startswith('2)'):continue
   target=fix(row['target']);raw=fix(row['amount']);name=fix(row['name']).replace(' ','');conditions=[]
   par=re.findall(r'\((?:단|다만)[^)]*\)',target);target=re.sub(r'\((?:단|다만)[^)]*\)','',target).strip()
   conditions.extend(fix(v).strip('()').replace('단, ','').replace('다만, ','')+'。' for v in par)
   condamt=re.search(r'\(\s*단.*',raw)
   if condamt:conditions.append(condamt[0].strip('()') .replace('단, ','')+'。')
   if '암보장개시일' in target:
    conditions.append('암 보장은 계약일(부활일)을 포함해 90일이 지난 다음 날부터 시작합니다.'+(' 갱신계약은 갱신일부터 보장하며 최초계약의 초기 감액을 다시 적용하지 않습니다.' if '갱신형' in title else ''))
   if '주요치료' in title:
    conditions.append('최초 진단일부터 10년간 연간 1회, 최대 10회 지급합니다. 연간은 최초 진단일부터 매 1년 단위이며 다른 대상 질환을 나중에 진단받아도 지급기간을 새로 시작하지 않습니다. 보험기간 종료 후에도 최초 진단일부터 10년 이내 해당 치료는 지급대상입니다.')
    if '뇌심' in title:target+=' 뇌심주요치료는 뇌심수술·혈전용해치료·중환자실치료입니다.'
    else:target+=' 주요치료는 암수술·항암약물치료·항암방사선치료입니다.'
    if '호르몬 관련 치료제는 보장하지' in notes:conditions.append('호르몬 관련 치료제는 주요치료 보장에서 제외됩니다.')
   if '생활자금' in title:
    conditions.append('최초 진단에 대해 첫 12개월은 확정 지급하고 이후 매년 진단해당일에 생존하면 그해 12개월을 확정 지급하며 최대 60개월입니다. 미지급 확정분은 할인한 일시금으로 받을 수 있습니다. 지급 개시 후 보험기간이 종료되어도 생존 요건을 충족하면 계속 지급합니다.')
    conditions.append('보장개시 후 사망하고 해당 질환이 직접 사망원인으로 확인되면 미지급 진단에 대해 사망일을 진단일로 보아 12개월분을 지급합니다.')
   if '건강검진지원' in title:conditions.append('첫 1년 확정 지급 후 매년 진단해당일 생존 시 연 1회 최대 10년 지급합니다. 지급 중 보험기간이 종료되어도 생존 요건을 충족하면 계속 지급합니다. 사망 후 보장대상 암이 직접 사망원인으로 확인되면 미지급 진단에 대해 첫 1년분만 지급합니다.')
   if '생존시지급' in title:conditions.append('진단일부터 5년이 되는 해당일에 생존해야 지급합니다. 진단 후 보험기간이 종료되어도 5년 생존 요건을 충족하면 지급하지만 5년 이전 사망에는 생존지원금을 지급하지 않습니다. 대상 질환을 진단받은 이후에는 갱신하지 않습니다.' if '갱신형' in title else '진단일부터 5년이 되는 해당일에 생존해야 지급합니다. 진단 후 보험기간이 종료되어도 5년 생존 요건을 충족하면 지급하지만 5년 이전 사망에는 생존지원금을 지급하지 않습니다.')
   if '소액암진단특약' in title and '갱신형' in title:conditions.append('기지급한 동일 소액암의 잔존·재발·전이는 갱신해도 추가 지급하지 않습니다. 지급 후 최초 갱신일부터 5년 동안 추가 진단·치료가 없으면 5년 경과 후 다시 보장하는 예외가 적용됩니다.')
   if '암진단특약Ⅴ' in title:target+=' 일반암은 기타피부암·중증 이외 갑상선암·대장점막내암을 제외하며 중증 갑상선암은 포함합니다.';conditions.append('최초 진단 1회 지급. 계약일부터 180일 미만에 진단된 유방암은 10%만 지급하며 나머지 90%를 나중에 추가 지급하지 않습니다.')
   if '암진단특약Ⅴ' in title:conditions=[v for v in conditions if '상기금액' not in v and v!='최초 1회에 한함。']
   if '입원특약' in title:
    if '간병인' in title or '간호간병' in title:conditions.append('실제 간병인 또는 간호·간병통합서비스를 사용한 날만 지급합니다. 유상 간병서비스와 간호·간병통합서비스를 구분하며 통합서비스 사용일에는 간병인사용 급여금을 중복 지급하지 않습니다.')
    if '계속입원 중에 1년 이상' in notes:conditions.append('1년 미만에 시작한 비재해 입원이 계속되어 계약 1년이 경과하면 그날부터 100%를 지급합니다.')
   if '질병' in title and '수술특약' in title:conditions.append('동일 질병(질병분류 3자리 동일)의 반복 수술은 1회만 지급하되 365일 경과 후 새로운 수술은 별도 지급합니다. 동시 수술은 원칙적으로 1회 지급하며 서로 다른 질병·신체부위·치료목적의 독립 수술은 각각 지급합니다. 미용·피임·검사만을 위한 수술은 제외됩니다.')
   if '허가치료' in title:
    if any(v in title for v in ['카티','면역항암','표적항암','항암호르몬']):conditions.append('식약처 허가 효능·효과 내 사용 또는 암질환심의위원회 심의를 거쳐 심평원이 승인한 요법을 해당 신청·신고 기관에서 사용해야 합니다. 약물의 처방만으로는 지급하지 않고 실제 투여가 필요합니다.')
    if '보험기간 이후에 약물을 투여' in notes:conditions.append('보험기간 내 처방을 받고 일정 협의 등으로 보험기간 후 투여한 경우에도 보장합니다.')
   if '고혈압' in title or '당뇨병' in title or '이상지질' in title:
    conditions.append('최초계약은 계약일부터 1년이 지난 계약해당일, 부활계약은 부활일부터 1년 지난 날부터 보장합니다.'+(' 갱신계약은 갱신일부터 보장합니다.' if '갱신형' in title else ''))
    if '당뇨' in title:target+=' 당뇨병 분류표의 질환 중 당화혈색소(HbA1c) 6.5% 이상을 만족하는 진단입니다.'
    else:conditions.append('처방일의 합이 누적 180일 이상이어야 합니다. 보장개시 후 진단되고 보험기간 내 처방요건을 일부 충족했다면 최종 보험기간 종료 후 누적 180일 충족도 지급대상입니다.')
   if '질병장해' in title:conditions.append('질병으로 발생한 장해를 장해분류표의 지급률로 판정합니다. 같은 질병의 여러 신체부위 장해는 합산하되 동일 부위의 중복 장해는 높은 지급률을 적용하고 합산은 100%를 한도로 합니다.')
   amount=amount_desc(raw,t['basis']);cname=rider+' / '+name
   if '1-5종수술' in title:
    for k in range(1,6):add(di,rider+f' / {k}종수술급여금',f'피보험자가 직접적인 치료를 목적으로 1~5종 수술분류표의 {k}종 수술을 받은 경우.',f'수술 1회당 {k}종 세부보장에 약정한 가입금액 100%. 1~5종별 가입금액은 서로 다를 수 있으며 해당 계약의 세부보장 금액으로 결정됩니다.','계약일부터 1년 미만 비재해 수술은 50%, 재해 수술은 100% 지급합니다. 동시 수술은 가장 높은 급여금 한 종류를 지급하되 서로 다른 신체부위·치료목적의 독립 수술은 각각 지급합니다. 미용·피임·가임 회복·검사 및 진단만을 위한 수술은 제외됩니다.',f'{start}–{t["page"]}')
    continue
   if name=='사망보험금':amount='사망 시 주계약 보험가입금액과 이미 납입한 보험료 중 큰 금액. 지급표는 가입금액 500만원 기준 사망보험금 500만원을 예시하며 실제 계약의 가입금액·납입보험료에 따라 달라집니다.';conditions=['보험기간 중 사망 시 지급하며 계약이 소멸합니다. 고의 자해·계약자 또는 수익자의 고의 가해는 미지급 사유이나 심신상실 상태의 자해 사망 및 보장개시(부활) 후 2년 경과 자살 등 약관상 예외가 적용됩니다.']
   if di==5 and any(v in title for v in ['암진단특약Ⅴ','뇌혈관질환진단특약Ⅱ','허혈성심장질환진단특약Ⅱ']) and '갱신형' not in title and '기본보장기간' in row['amount']:
    cname+='(집중보장형)';amount='집중보장형: 계약일부터 10년 경과시점 전까지 가입금액 100%, 10년 경과시점 계약해당일부터 가입금액 200%. 가입금액 1,000만원 예시에서는 각각 1,000만원/2,000만원입니다.'
   elif di==5 and any(v in title for v in ['암진단특약Ⅴ','뇌혈관질환진단특약Ⅱ','허혈성심장질환진단특약Ⅱ']) and '갱신형' not in title:cname+='(기본형)'
   if '항암방사선약물치료특약' in title:cname+=' / '+('소액암(기타피부암·갑상선암·대장점막내암)' if '대장점막' in target else '일반암')
   cond=' '.join(dict.fromkeys(conditions)).replace('。','.').strip();cond=fix(cond)
   if not cond:cond='보험기간 중 해당 지급사유가 발생해야 하며 지급표에서 정한 최초 1회 또는 회당 지급기준을 적용합니다.'
   add(di,cname,'피보험자: '+target,amount,cond,f'{start}–{min(t["page"]+1,end)}')
 # Insurance premium waiver benefits without payout tables
 for printed,title in toc(di):
  if not title.startswith('보험료납입면제특약'):continue
  st=printed+(30 if di==3 else 29);en=section(di,st)[2];typ='1형' if '1형' in title else '2형'
  target='피보험자가 암보장개시일 이후 일반암으로 진단확정된 경우. 기타피부암·중증 이외 갑상선암·대장점막내암은 제외하고 중증 갑상선암은 포함합니다.' if typ=='1형' else '피보험자가 보험기간 중 발생한 동일 재해로 여러 신체부위 장해지급률 합계 50% 이상인 장해상태가 된 경우. 질병 장해를 대상으로 하지 않습니다.'
  add(di,title+' / 보험료납입면제',target,'현금 보험금 지급이 아니라 납입면제대상 주계약·특약의 차회 이후 보험료 전액을 면제합니다. 면제액은 실제 계약의 잔여 납입보험료에 따라 결정됩니다.','부가 시 비갱신형 주계약·특약 중 이 특약의 보험기간 및 납입기간과 대상계약의 납입기간이 같은 계약에 적용합니다. 다른 면제사유 특약·같은 사유로 이미 면제되는 계약·면제사유 발생 시 소멸되는 계약은 제외합니다. '+('암 보장개시는 계약일(부활일) 포함 90일 경과 다음 날입니다.' if typ=='1형' else '동일 재해의 장해는 합산하되 동일 부위의 중복 장해는 높은 지급률을 적용합니다. 장해가 180일 내 확정되지 않으면 180일째 의사 진단에 따른 고정 상태를 기준으로 판정합니다.'),f'{st}–{min(st+6,en)}')
 # special payment methods linked to existing death benefit
 off=30 if di==3 else 29
 for printed,title in toc(di):
  if title=='사후정리특약':add(di,'사후정리특약 / 사망보험금 사후정리 지급','주계약·특약 피보험자가 보험기간 중 보장개시 후 사망한 경우의 해당 사망보험금 수익자.','기존 주계약·특약의 비재해 사망보험금 일부 또는 전부를 해당 수익자의 사망보험금 지급비율에 따른 한도 안에서 지급합니다. 별도의 추가 보험금을 더하는 담보는 아닙니다.','뚜렷한 사기의사 등으로 보험금 지급책임이 없다고 판단되면 지급하지 않습니다. 먼저 지급한 금액은 잔여 사망보험금 정산에서 반영합니다.',f'{printed+off+1}–{printed+off+2}')
  if title=='선지급서비스특약 무배당':add(di,'선지급서비스특약 무배당 / 선지급사망보험금','국내 종합병원 또는 해외 법정 의료기관의 전문의 진단으로 잔여수명이 12개월 이내라고 판단된 주계약 피보험자.','지급일 현재 주계약 사망보험금 일부 또는 전부에서 여명기간 상당 이자·보험료 및 보험계약대출 원리금을 차감한 금액. 선지급액 상당 가입금액을 감액하므로 추가 사망보험금이 아닙니다.','주계약 사망보험금이 먼저 청구되거나 지급되면 선지급하지 않습니다. 지급 후 동일 금액의 사망보험금·감액분 해약환급금을 중복 지급하지 않습니다. 계약자·지정대리청구인의 고의로 지급사유가 발생하면 제외합니다.',f'{printed+off+1}–{printed+off+4}')
# mirror proven identical rider body to plus products; sources point to respective PDFs
for base,plus in [(3,7),(5,9)]:
 assert P[base][55:1262]==P[plus][55:1262] if base==3 else P[base][54:1340]==P[plus][54:1340]
 for r in list(records):
  if r['source_file']!=M[base]['path']:continue
  x=copy.deepcopy(r);x['id']=len(records)+1;x['product_name']=re.sub(r'^판매중__20250701_','',M[plus]['product']).replace('_',' ');x['source_file']=M[plus]['path'];x['business_file']=M[plus-1]['path'];x['review']+=' 기본형과 특약 본문 전 페이지 동일 확인; 플러스형 원문으로 출처 연결.';records.append(x)
# MAX whole-life, conversion and death payment methods
di=1
add(di,'주계약 / 체증형 사망보험금','피보험자가 종신 보험기간 중 사망한 경우.','계약일부터 5년 경과시점 전까지 가입금액 100%. 5년 경과 계약해당일부터 매년 가입금액의 20%씩 체증하여 25년 경과 계약해당일부터 종신까지 가입금액의 500%. 가입금액 1억원 예시: 최초 1억원, 5년 경과부터 연 2,000만원씩 증가, 25년 경과 후 5억원.','매년 계약해당일의 체증금액을 1년간 확정 적용합니다. 보험가입금액 감액·연금선지급제도 이용 시 변경된 가입금액이 반영됩니다. 고의 자해·계약자 또는 수익자의 고의 가해는 제외하되 심신상실 자해 사망 및 보장개시(부활) 후 2년 경과 자살 등 약관상 예외가 적용됩니다.','24–25, 44')
add(di,'주계약 / 사망보험금 연금선지급금','최초 선지급일 나이 55~90세인 피보험자가 선택한 연금선지급기간의 매년 지급해당일에 생존한 경우.','연간 감액액=선택한 연금선지급 대상 가입금액÷지급기간(연수). 매년 선지급금=선지급 직전 해약환급금×연간 감액액÷선지급 직전 가입금액. 사망보험금 자체를 지급기간으로 나눈 금액이 아니라 감액부분의 해약환급금입니다.','보험료 납입기간·체증기간이 끝나고 최초 지급일 해약환급금 1,000만원 이상이며 대출 원리금 잔액이 없어야 합니다. 가입금액 90% 이내 대상 금액과 5~20년 지급기간 선택. 1회 신청 가능하며 중지 후 재신청 불가. 사망 등 계약 효력 종료 시 선지급 종료. 감액 부분은 해지된 것으로 보아 잔여 사망보험금이 줄어듭니다.','40–41, 45')
add(di,'주계약 / 동일 재해 50% 이상 장해 보험료납입면제','보험료 납입기간 중 동일 재해로 여러 신체부위 장해지급률 합계가 50% 이상인 피보험자.','차회 이후 주계약 보험료 전액 면제. 현금 지급액이 아니라 계약별 잔여 보험료에 대한 면제입니다.','보험료 납입기간 중 재해장해로 요건을 충족해야 합니다. 같은 신체부위의 중복 장해는 높은 지급률을 적용하며 약관 장해분류표로 판정합니다.','24–25, 44')
for n,t,a,c,p in [
 ('연금전환특약(거치형) / 연금개시 전 재해장해보험금','전환 후 연금개시 전 기간 중 동일 재해로 장해지급률 합계가 80% 이상인 피보험자.','월 50만원씩 36회 확정 지급(총 1,800만원). 가입금액 비례 지급으로 표시되어 있지 않은 정액 보장입니다.','최초 1회 지급. 연금개시 전은 전환일부터 연금개시일 전일까지이며 동일 재해 장해를 약관 장해분류표로 판정합니다.','86–87, 95'),
 ('연금전환특약(거치형) / 연금개시 전 사망 지급금','전환 후 연금개시 전에 사망한 피보험자. 지급받는 자는 계약자.','이미 납입한 보험료(적립액 인출이 있으면 인출액 차감)와 사망 당시 계약자적립액 중 큰 금액.','연금개시 전 사망 시 특약이 소멸합니다.','89, 95'),
 ('연금전환특약(거치형) / 확정연금','연금개시 후 선택한 확정지급기간의 매년 계약해당일. 생존 여부와 관계없이 확정기간의 지급대상.','연금개시 시 계약자적립액을 기준으로 선택한 확정지급기간 10·20·30·40·50년에 따라 산출한 연금액. 공시이율에 따라 변동하므로 고정 원화액은 없습니다.','확정기간 내 사망해도 미지급 연금은 정해진 지급일에 지급합니다. 회사 승낙으로 잔여 확정분을 공시이율로 할인해 선지급할 수 있습니다.','96–97'),
 ('연금전환특약(거치형) / 상속연금','연금개시 이후 종신 기간 중 매년 계약해당일에 생존한 피보험자.','연금개시 시 계약자적립액을 기준으로 산출한 연금액. 공시이율 변동을 반영하며 사망 시에는 사망시점 계약자적립액 지급.','생존 시 연금 지급, 사망 시 적립액 지급 후 계약 종료.','96–97'),
 ('연금전환특약(거치형) / 상속연금 사망 지급금','상속연금 개시 후 피보험자가 사망한 경우.','사망시점 계약자적립액 전액.','상속연금형에 해당하는 사망 지급금이며 별도 정액 사망보험금을 추가 지급하지 않습니다.','96'),
 ('연금전환특약(거치형) / 종신연금','연금개시 이후 매년 계약해당일에 생존한 피보험자. 보증지급기간은 10·20·30년 또는 100세.','연금개시 시 계약자적립액·연금사망률·선택한 보증기간을 반영하여 산출한 연금액. 공시이율에 따라 변동하는 연금으로 고정 원화액은 없습니다.','보증기간 내 사망해도 미지급 보증분은 정해진 지급일에 지급합니다. 회사 승낙으로 잔여 보증분을 할인해 선지급할 수 있습니다. 종신연금 개시 후에는 해지할 수 없습니다.','91, 96–97')]:
 common=' 전환 전 가입일부터 7년 경과, 해약환급금이 이미 납입한 보험료 이상, 만기(연금개시)까지 2년 이상 남은 계약에서 전환할 수 있습니다. 전환일부터 전환 전 계약의 해당 보장은 효력을 잃습니다.'
 rate=' 최저보증이율은 전환 전 가입일부터 경과기간 3년 이내 연복리 1.75%, 3~5년 1.25%, 5~10년 1.15%, 10년 초과 0.5%. 연금은 월·3개월·6개월 분할 지급 가능.' if '연금개시 전 재해' not in n else ''
 add(di,n,t+' 전환 피보험자는 전환 전 피보험자 또는 그 배우자·자녀 중 1명입니다.',a,c+common+rate,p+', 89',review='전환 지급표 및 피보험자 범위·전환조건·공시이율 조항 대조.')
for sourcebase in [3]:
 for r in list(records):
  if r['source_file']!=M[sourcebase]['path'] or not r['coverage_name'].startswith(('사후정리특약','선지급서비스특약')):continue
  add(di,r['coverage_name'],r['coverage_target'],r['coverage_amount'],r['coverage_conditions'],'73–74' if r['coverage_name'].startswith('사후') else '78–81')
for i,r in enumerate(records,1):r['id']=i
seen=set();unique=[]
for r in records:
 k=(r['product_name'],r['coverage_name'],r['coverage_target'],r['coverage_amount'])
 if k in seen:print('DUPLICATE',r['coverage_name'],r['source_page']);continue
 seen.add(k);unique.append(r)
records=unique
for i,r in enumerate(records,1):r['id']=i
(R/'records.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8');(R/'audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf8')
from collections import Counter
print(len(records),dict(Counter(r['product_name'] for r in records)))
