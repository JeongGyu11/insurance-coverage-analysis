import json,re
from pathlib import Path
from datetime import datetime,timezone,timedelta
R=Path('work/heungkuk_life');M=json.loads((R/'manifest.json').read_text(encoding='utf8'));T=json.loads((R/'tables.json').read_text(encoding='utf8'));S=json.loads((R/'sections.json').read_text(encoding='utf8'));P={i:json.loads((R/f'doc{i}.json').read_text(encoding='utf8')) for i in [1,3,5]}
stamp=datetime.now(timezone(timedelta(hours=9))).isoformat(sep=' ',timespec='seconds');rows=[];audit=[]
def c(s):return re.sub(r'\s+',' ',s or '').strip()
def compact(s):return re.sub(r'\s+','',s)
def section(di,p):
 sec=[s for s in S[str(di)] if s['page']<=p][-1];nxt=[s['page'] for s in S[str(di)] if s['page']>sec['page']];en=min(nxt)-1 if nxt else (96 if di==1 else 765 if di==3 else 459)
 title=sec['title'].split(' 무배당 ')[0].replace(' 보통보험약관','').replace(' 약관','')
 return title,sec['page'],en,c(' '.join(P[di][sec['page']-1:en]))
def notes(t):
 tx=c(t);idx=tx.find('주)')
 if idx<0:return []
 tx=tx[idx+2:];tx=re.split(r'\s-\s[12]종|\s[12]\)\s*(?:홈케어|시설입소)',tx)[0]
 a=re.split(r'(?<!\d)\b\d{1,2}\.\s',tx)
 return [c(v) for v in a if len(c(v))>3]
def article(body,name):
 matches=list(re.finditer(r'제\s*\d+\s*조\s*【([^】]+)】',body))
 for i,z in enumerate(matches):
  if name in compact(z[1]):
   text=body[z.end():matches[i+1].start() if i+1<len(matches) else len(body)]
   if text.lstrip().startswith('·'):continue
   return text
 return ''
def money(s):
 z=re.search(r'([\d,.]+)\s*만\s*원',s)
 return float(z[1].replace(',','')) if z else None
def add(di,title,name,target,amount,cond,page,start=None):
 prod=re.sub(r'^판매중__\d+_','',M[di]['product']);prod=re.sub(r'_row\d+$','',prod)
 rows.append(dict(id=len(rows)+1,company_name='흥국생명',product_name=prod,coverage_name=name,coverage_target=c(target),coverage_amount=c(amount),coverage_conditions=c(cond),created_at=stamp,updated_at=stamp,source_file=M[di]['path'],source_page=str(page),business_file=M[di-1]['path'],business_page='1–'+str(M[di-1]['pages']),review='약관 지급기준표와 해당 특약 본문 대조. 실제 계약금액은 가입금액·가입형 및 지급사유에 따라 결정.',section_start=start or page))
for x in T:
 di,pg=x['doc'],x['page'];title,st,en,body=section(di,pg);N=notes(x['text']);audit.append(dict(doc=di,page=pg,section=title,tables=len(x['tables'])))
 for tab in x['tables']:
  before=c(tab['before']);bz=re.findall(r'\[기준\s*[:：]\s*([^\]]+)\]',before);basis=bz[-1] if bz else ''
  labels=re.findall(r'(?:\[|-\s*)([12]종\([^)]*\))|\[(최초계약|갱신계약)\]|([12]\)\s*(?:시설입소|홈케어)보장계약)',before)
  label=next((next(v for v in z if v) for z in reversed(labels)), '')
  if not label and '갱신형' in title:
   z=re.findall(r'(최초계약|갱신계약)',before)
   if z:label=z[-1]
  # Notes after this specific table, ending at the next table header/variant.
  groups=[];prevname='';prevcause=''
  for rr in tab['rows'][1:]:
   if len(rr)<3:continue
   vals=[c(v) for v in rr]
   if vals[0]:prevname=vals[0]
   if vals[1]:prevcause=vals[1]
   if not prevname or not prevcause:continue
   name=re.sub(r'\((?:약관\s*)?제\d+조[^)]*\)','',prevname);name=compact(name)
   cause=prevcause
   branches=[v for v in vals[2:-1] if v]
   amt=vals[-1]
   if not amt:amt=' '.join(branches);branches=[]
   if not amt:continue
   branch=' '.join(branches)
   if len(rr)==4 and compact(rr[:1][0] or '')=='':pass
   # Four-column tables use either an amount-band or a target subgroup.
   targetbranch= len(rr)==4 and (tab['rows'][0][2] is None) and compact(tab['rows'][0][1])=='지급사유'
   if targetbranch and branch:cause+=' '+branch;branch=''
   if groups and groups[-1]['name']==name and groups[-1]['cause']==cause:
    groups[-1]['amounts'].append((branch,amt))
   else:groups.append(dict(name=name,cause=cause,amounts=[(branch,amt)]))
  for g in groups:
   name=g['name'];cause=g['cause'];conds=[]
   par=re.findall(r'\((?:다만|최초|수술\s*1회|동일한\s*질병당|발생\s*1회)[^)]*\)',cause)
   for z in par:conds.append(z.strip('()').replace('다만,','').strip()+'.')
   target=re.sub(r'\((?:다만|최초|수술\s*1회|동일한\s*질병당|발생\s*1회)[^)]*\)','',cause).strip()
   if not target.startswith('피보험자'):target='피보험자: '+target
   targetdefs=[];selected=[]
   for n in N:
    if any(z in n for z in ['보험료 납입기간','특약은 그 때부터','계약자적립액','계약을 무효','특약을 무효','이 계약은 그 때부터','계약을 해지할 수','특약을 해지할 수']):continue
    if re.search(r'^(?:소액암|경도치매상태|중등도치매상태|중증치매상태|경증이상장기요양상태|중등도이상장기요양상태|중증이상장기요양상태|시니어특정질환|2대질병|암 주요치료|2대질병 주요치료|하이클래스[^:]{0,25})\s*[:：]',n):
     targetdefs.append(n);continue
    if '보장개시일' in n:
     # Only include the waiting period of the benefit actually being covered.
     if '암보장개시일' in n and '암보장개시일' not in target:continue
     if '장기요양상태보장개시일' in n and '장기요양상태보장개시일' not in target:continue
     if '치매보장개시일' in n and '치매보장개시일' not in target:continue
    if any(z in n for z in ['보장개시일','支給','지급','한도','제외','보장하지','보상하지','180일','연간','전액본인부담','정의','처방','시간','일수','기간','제한']):
     selected.append(n)
   # Compact major repeated operative notes.
   for n in selected:
    if '암보장개시일' in n and '90일' in n and '두 번째' not in n:
     n='암 보장은 계약일(부활일)을 포함하여 90일이 지난 다음 날부터 시작합니다.'+(' 갱신계약은 갱신일부터 보장합니다.' if '갱신계약' in n else '')
    elif '치매보장개시일' in n and '1년' in n:
     n='치매 보장은 계약일(부활일)을 포함하여 1년이 되는 날의 다음 날부터 시작합니다. 재해로 인한 뇌 손상이 직접 원인인 치매는 계약일(부활일)부터 보장합니다.'
    elif '장기요양상태보장개시일' in n and '90일' in n:
     n='장기요양 보장은 계약일(부활일)을 포함하여 90일이 되는 날의 다음 날부터 시작합니다. 재해가 직접 원인이면 계약일(부활일)부터 보장합니다.'
    elif '최초계약' in n and '감액' in n and '갱신계약' in n:n='최초계약의 초기 감액은 갱신계약에 다시 적용하지 않습니다.'
    elif '동일한 질병을 직접적인 원인' in n and '365일' in n:n='동일 질병(질병분류번호 3자리 동일)의 수술은 1회 지급하되, 수술 후 365일이 지나 새로 받은 수술은 별도 지급합니다.'
    elif '식품의약품안전처' in n and '효능효과' in n:
     n='식약처 허가 효능·효과 내 사용 또는 암질환심의위원회 심의를 거친 심평원 승인 요법을 해당 신청·신고 요양기관에서 사용해야 합니다. 처방 시점의 허가 기준을 적용합니다.'
    elif '연간' in n and '매1년' in compact(n):
     n='연간은 '+('최초 진단확정일부터' if '진단확정일' in n else '계약일부터')+' 매 1년 단위로 계산합니다.'
    n=re.sub(r'제\d+조\([^)]*\)(?:\s*제\d+항)?','약관',n)
    conds.append(n)
   target+=' '+' '.join(dict.fromkeys(targetdefs))
   raw='; '.join((b+': ' if b else '')+a for b,a in g['amounts'])
   denominator=money(basis)
   rates=[]
   if denominator:
    for b,a in g['amounts']:
     v=money(a)
     if v is not None:rates.append((b+': ' if b else '')+f'가입금액의 {v/denominator*100:g}%')
   amount=((' / '.join(rates)+'. ') if rates else '')+f'지급표 기준: {basis or "해당 계약의 가입금액"}. 지급액: {raw}.'
   if denominator:amount+=' 지급표 금액은 기준 가입금액의 예시이며 실제 계약 가입금액에 비례하여 계산합니다.'
   if '장해지급률' in raw:amount=f'해당 계약 가입금액 × 장해분류표의 장해지급률. 지급표 기준: {basis}; {raw}.'
   cname=title+' / '+name+(' / '+label if label else '')
   # special primary life benefits
   if di==1 and pg in [36,37]:
    typ='1종(생활자금집중형)' if pg==36 else '2종(사망보장강화형)'
    cname='주계약 / '+name+' / '+typ
    if name=='사망보험금':
     target=cause
     amount='암진단 생활자금 지급사유가 없으면 가입금액의 100%, 발생했으면 50%와 이미 납입한 보험료 중 큰 금액. 생활자금 발생 후 이미 납입한 보험료는 실제 지급한 생활자금과 '+('36회' if pg==36 else '60회')+' 보증지급 해당액 중 큰 금액을 차감하여 산정합니다.'
     conds=['종신 보장. 사망보험금 지급 시 주계약이 소멸합니다.']
    else:
     amount=f'매월 가입금액의 {50/(4000 if pg==36 else 10000)*100:g}%. 가입금액 {4000 if pg==36 else 10000:,}만원 기준 매월 50만원, 최대 120회 지급.'
     conds=['계약일(부활일) 포함 90일 경과 다음 날부터 암 보장. 최초 진단에 한해 10년간 지급하며 최초 '+('36회' if pg==36 else '60회')+'는 보증지급합니다. 이후 매년 진단해당일에 생존하면 해당 연도 12회를 확정 지급합니다. 보증기간 중 사망하면 잔여 보증금액을 지급합니다. 갑상선암·기타피부암은 제외됩니다.']
   if name=='사망보험금' and di==5:
    amount+=' 약관상 지급액과 이미 납입한 주계약 기본보험료 중 큰 금액을 지급합니다. 비재해 사망이 계약일부터 2년 미만이면 사망 시점의 이미 납입한 보험료를 지급합니다.'
   if name=='치매예방프로그램현물급부':
    amount='치매예방프로그램을 현물로 제공합니다. 제공 불가 또는 피보험자의 이용 불가·이용 의사 없음인 경우 현금으로 대체하며, 특약가입금액 100만원 기준 현금 100만원입니다.'
    conds=[v for v in conds if '제6호' not in v and '아래의 사유' not in v]
   if '바로보장형' in label:conds=[v for v in conds if '장기요양 보장은' not in v]
   if '갱신계약'==label:
    amount=re.sub(r'최초계약[^.]*\.','',amount)
    conds=[v for v in conds if '초기 감액' not in v]
    if '암보장개시일' in target:conds=[v for v in conds if not v.startswith('암 보장은')]+['갱신일부터 암을 보장하며 최초계약의 초기 감액은 적용하지 않습니다.']
   if '1~5종재해수술' in title:
    for kind,value in re.findall(r'([1-5]종)\s*:\s*([\d,]+)만원',raw):
     add(di,title,cname+' / '+kind,target+f' {kind} 수술분류에 해당하는 수술.',f'수술 1회당 가입금액의 {int(value.replace(",",""))/denominator*100:g}%. {basis} 기준 {value}만원. 실제 계약 가입금액에 비례하여 계산합니다.',' '.join(dict.fromkeys(conds)),pg,st)
    continue
   add(di,title,cname,target,amount,' '.join(dict.fromkeys(conds)),pg,st)
# Explicit premium waiver riders (no cash payout table)
for di in [3,5]:
 for sec in S[str(di)]:
  if '납입면제' not in sec['title']:continue
  title,st,en,body=section(di,sec['page']);pay=article(body,'납입면제사유');det=article(body,'보험료납입면제에관한세부규정')
  if not pay:raise ValueError(title)
  pay=c(pay).replace('회사는','').strip()
  pay=re.sub(r'\(별표[^)]*\)','',pay)
  target='피보험자: '+pay
  cond='현금 보험금이 아닌 납입면제이며, 약관에서 정한 면제대상 주계약·특약의 차회 이후 보험료에 적용합니다.'
  if '암보장개시일' in pay:cond+=' 암 보장은 계약일(부활일) 포함 90일 경과 다음 날부터 시작합니다.'
  if di==5:cond+=' 장기요양 1~5등급 판정이 대상이며 계약일(부활일) 포함 90일 경과 다음 날부터 보장합니다. 재해가 직접 원인이면 계약일(부활일)부터 보장합니다.'
  add(di,title,title+' / 보험료납입면제',target,'납입면제대상 계약의 차회 이후 보험료 전액. 실제 면제금액은 해당 계약의 잔여 보험료로 결정됩니다.',cond,f'{st}–{min(st+10,en)}',st)
# Main contract waiver from explicit payout-table notes
for di,pg in [(1,36),(3,44),(5,59)]:
 title,st,en,body=section(di,pg)
 cond='보험료 납입기간 중 지급사유가 발생해야 합니다. 장해는 동일 재해 또는 재해 이외의 동일 원인의 여러 신체부위 장해지급률을 합산합니다.'
 target='주계약 피보험자가 동일 재해 또는 재해 이외의 동일 원인으로 장해지급률 합계 50% 이상이 된 경우.'
 if di==1:target+=' 또는 암보장개시일 이후 암진단 생활자금 지급사유가 발생한 경우.';cond+=' 암 보장개시는 계약일(부활일) 포함 90일 경과 다음 날입니다.'
 add(di,title,'주계약 / 보험료납입면제',target,'차회 이후 주계약 보험료 납입을 면제합니다. 현금 지급이 아니며 면제금액은 실제 계약의 잔여 보험료로 결정됩니다.',cond,pg,st)
# Coverage completeness against every benefit section (system riders excluded).
covered={(r['source_file'],r['section_start']) for r in rows}
for di in [1,3,5]:
 for s in S[str(di)]:assert (M[di]['path'],s['page']) in covered,(di,s)
for r in rows:assert all(r[k] for k in ['company_name','product_name','coverage_name','coverage_target','coverage_amount'])
(R/'records.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
(R/'audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf8')
print('ROWS',len(rows));print('PRODUCTS',[(p,len([r for r in rows if r['product_name']==p])) for p in dict.fromkeys(r['product_name'] for r in rows)])
for r in rows:
 if len(r['coverage_conditions'])>1200:print('LONG',r['id'],len(r['coverage_conditions']),r['coverage_name'])


# Semantic corrections after merged-cell extraction and compact, operative descriptions.
rows=[r for r in rows if not r['coverage_name'].endswith('/ 세부보장(종)')]
src={(x['doc'],x['page']):x for x in T}
replacements={'보 장':'보장','금 액':'금액','지 급':'지급','면 제':'면제','정 의':'정의','진단확 정':'진단확정','진단확정되 었':'진단확정되었','장기요양상태보 장개시일':'장기요양상태보장개시일','장기요양상태보장개 시일':'장기요양상태보장개시일','경증 이상':'경증이상','중증 이상':'중증이상','시니어특정질환보장개 시일':'시니어특정질환보장개시일','직접 적인':'직접적인','뇌혈관 질환':'뇌혈관질환','신체부 위':'신체부위','관상동맥(심장동맥)촬영 술':'관상동맥(심장동맥)촬영술','전 이':'전이','보 장':'보장','또 는':'또는','통 합':'통합','입 원':'입원','간호·간병통 합':'간호·간병통합','단, 계약일로부터 2년 미만':'단, 계약일로부터 2년 미만'}
def norm(s):
 for a,b in replacements.items():s=s.replace(a,b)
 return c(s)
def aname(s):return re.sub(r'[\s“”’"「」]','',s)
def getarticle(body,term):
 matches=list(re.finditer(r'제\s*\d+\s*조\s*【([^】]+)】',body))
 for i,z in enumerate(matches):
  if term in aname(z[1]):
   tx=body[z.end():matches[i+1].start() if i+1<len(matches) else len(body)]
   if not tx.lstrip().startswith('·'):return norm(tx)
 return ''
for r in rows:
 di=next(i for i in [1,3,5] if M[i]['path']==r['source_file']);pg=int(r['source_page'].split('–')[0])
 title,st,en,body=section(di,pg);body=norm(body);name=r['coverage_name'];target=norm(r['coverage_target']);cond=norm(r['coverage_conditions']);amt=norm(r['coverage_amount'])
 if (di,pg) in src:
  tx=norm(src[di,pg]['text']);nt=notes(tx)
  # Remove premium waiver clauses and duplicate limit prose from cash payout rows.
  parts=[]
  for n in nt:
   if '보험료' in n and ('면제' in n or '납입' in n):continue
   if any(z in n for z in ['특약은 그 때부터','계약자적립액','계약을 무효','특약을 무효','이 계약은 그 때부터','계약을 해지할 수','특약을 해지할 수']):continue
   parts.append(norm(n))
  # Remove extracted premium-waiver prose already in conditions.
  cond=re.sub(r'(?:주계약의 보험료 납입이 면제된 경우|보험료 납입기간 중)[^.]*면제[^.]*\.?','',cond)
  cond=cond.replace('동 약관 약관','약관')
  # Waiting period detection uses full payout text so extraction line wrapping cannot hide it.
  flat=compact(tx);tar=compact(target)
  if '장기요양상태보장개시일' in tar and '90일' in flat and '바로보장형' not in name and '장기요양 보장은' not in cond:
   cond+=' 장기요양 보장은 계약일(부활일) 포함 90일 경과 다음 날부터이며 재해가 직접 원인이면 계약일(부활일)부터입니다.'
  if '치매보장개시일' in tar and '1년' in flat and '치매 보장은' not in cond:
   cond+=' 치매 보장은 계약일(부활일) 포함 1년이 되는 날의 다음 날부터입니다. 재해로 인한 뇌 손상이 직접 원인이면 계약일(부활일)부터입니다.'
  # Monetary unit and count belong with the formula.
  unit='매월 ' if '매월' in amt else '1일당 ' if '입원급여금' in name else '통원 1일당 ' if '치매통원급여금' in name else '수술 1회당 ' if ('수술급여금' in name or '수술비' in name) else ''
  if unit and amt.startswith('가입금액'):amt=unit+amt
  if '장해지급률' in amt:
   basis=money(re.search(r'지급표 기준: ([^;]+)',amt)[1]);actual=money(amt.split(';')[-1])
   if basis and actual:amt=f'해당 계약 가입금액 × {actual/basis:g} × 해당 장해지급률. '+amt.split('. ',1)[-1]
  if '재해 이외의 원인' in tx and '50%' in tx and '1년 미만' in tx and '입원' in name:
   cond+=' 계약일부터 1년 미만에 발생한 비재해 입원 지급사유는 정상 지급액의 50%를 지급하며 재해 입원은 감액하지 않습니다.'
  # Move payout limits out of target into conditions.
  limits=re.findall(r'\((?:[^()]*?(?:한도|1회한)[^()]*)\)',target)
  for lim in limits:
   cond+=' '+lim.strip('()')+'.';target=target.replace(lim,'')
  # Precise target definitions and concise cash limits.
  if '2대질병' in name:
   target+=' 2대질병은 약관 분류표의 뇌혈관질환·허혈성심장질환입니다.'
   if '외상성 두개내 출혈' in body:cond+=' 외상성 두개내 출혈·혈관성 치매·과거 무증상성 열공성 뇌경색증은 제외됩니다.'
  if '주요치료' in name:
   if '2대질병' in name:target+=' 주요치료는 해당 질환의 수술·혈전용해치료·종합병원 중환자실치료입니다.'
   elif '특정순환계질환' in name:
    target+=' 주요치료는 특정순환계질환(3~5군)의 수술·혈전용해치료·종합병원 중환자실치료입니다.'
   elif '암' in name and '항암호르몬' not in name:target+=' 암 주요치료는 암수술·항암약물치료·항암방사선치료입니다.'
  if '소액암' in name and '소액암New' not in name and '갑상선암, 기타피부암, 제자리암, 경계성종양' not in target:
   definition=re.search(r'소액암\s*:\s*([^.]*)',tx)
   if definition:target+=' 소액암: '+definition[1].strip()+'.'
  if '당뇨병진단' in name:
   z=getarticle(body,'당뇨병의정의')
   if '6.5' in z:target+=' 약관 분류표의 당뇨병 중 당화혈색소(HbA1c) 6.5% 이상에 해당하는 진단입니다.'
  if '치매' in name and di==5:
   cdr=re.search(r'CDR척도\s*검사\s*결과가\s*([\d.]+)점\s*이상',tx)
   if cdr and 'CDR' not in target:target+=f' 해당 치매상태는 CDR척도 {cdr[1]}점 이상입니다.'
   if '정신 질환' in body and '알콜중독' in body:
    cond+=' 정신질환, 알콜중독 또는 의사 처방 없이 투여한 약물로 인한 인지기능 장애는 제외됩니다.'
  if '장기요양' in name and di==5:
   z='1~5등급' if '경증이상' in name else '1~3등급' if '중등도이상' in name else '1~2등급' if '중증이상' in name else ''
   if z and z not in target:target+=' 국민건강보험공단 등급판정위원회에서 판정한 장기요양 '+z+'가 대상입니다.'
  if '시니어특정질환' in name:
   z=getarticle(body,'시니어특정질환의정의')
   first=re.split(r'②',z)[0]
   target+=' '+first
  if '질병수술' in name and ('특정7대' in name or '특정질병제외' in name):
   z=getarticle(body,'질병의정의')
   excluded=re.findall(r'다만[^②]*',z)
   if excluded:cond+=' '+excluded[0][:650]
  if di==1 and pg in [36,37] and '사망보험금' in name:
   amt='암진단 생활자금 발생 전에는 가입금액 100%, 발생 후에는 가입금액 50%를 기준 사망보험금으로 하여, 이 금액과 약관상 이미 납입한 보험료 중 큰 금액을 지급합니다. 생활자금 발생 후 납입보험료 산정액에서는 기지급 생활자금과 '+('36회' if pg==36 else '60회')+' 보증지급 해당액 중 큰 금액을 차감합니다.'
  if di==3 and pg==44:
   target=target.replace('사망하였을 때','사망한 경우')
   if '재해 이외' in target:r['coverage_name']+=' / 비재해 사망'
   else:r['coverage_name']+=' / 재해 사망'
   amt+=' 위 기준 사망보험금과 약관상 이미 납입한 주계약 보험료 중 큰 금액을 지급합니다.'
   cond='사망 시 계약 소멸. 납입면제 기간에도 주계약 보험료가 정상 납입된 것으로 계산합니다.'+(' 계약일부터 2년 이내 비재해 사망은 사망 시점의 이미 납입한 보험료를 지급합니다.' if '재해 이외' in target else '')
  if di==5 and pg==59:
   r['coverage_name']+=' / '+('비재해 사망' if '이외' in target else '재해 사망')
  # Shorten service timing without removing substantive limits.
  if di==5 and '월계약해당일부터' in compact(cond):
   waiting='계약일(부활일) 포함 90일 경과 다음 날부터 보장하며 재해는 계약일(부활일)부터입니다. ' if '바로보장형' not in name else '계약일(부활일)부터 보장합니다. '
   cond=waiting+'월계약해당일부터 다음 월계약해당일 전일까지 실제 해당 급여를 이용하면 월 1회 지급합니다. 보험기간 종료 후 이용은 제외합니다. 노인장기요양보험법에 따라 급여 이용이 제한된 경우 지급하지 않습니다.'
  if '간병인사용' in name:
   limit=re.search(r'(\d+)일\s*한도',tx)
   startday='간병인 사용 181일째부터 ' if '181일이상' in name else '간병인 사용 첫날부터 '
   cond=startday+('입원 1회당 '+limit[1]+'일 한도. ' if limit else '')+'1일 8시간 이상 실제 간병서비스를 이용한 날만 지급하며 간호·간병통합서비스는 제외합니다. 계약 1년 미만 비재해 입원은 50%, 재해 입원은 100% 지급합니다. 보험기간 종료 시 계속 중인 입원은 약관상 한도 내에서 보장합니다.'
  if '간호간병통합서비스입원' in name:
   limit=re.search(r'(\d+)일\s*한도',tx)
   cond=('서비스 사용 181일째부터 ' if '181일이상' in name else '서비스 사용 첫날부터 ')+('입원 1회당 '+limit[1]+'일 한도. ' if limit else '')+'실제 간호·간병통합서비스 사용일만 지급합니다. 계약 1년 미만 비재해 입원은 50%, 재해 입원은 100% 지급합니다. 보험기간 종료 시 계속 중인 입원은 약관상 한도 내에서 보장합니다.'
  if '첫날부터' in name:
   limit=re.search(r'(\d+)일\s*한도',tx)
   cond='치료 목적의 계속입원을 첫날부터 보장합니다.'+(' 입원 1회당 '+limit[1]+'일 한도.' if limit else '')
  if di==3 and pg==592:
   z=re.search(r'/ (\d+)종:',name)
   assert z,name
   kind=int(z[1]);r['coverage_name']=title+' / 통합암항암약물방사선치료비 / '+name.split('/ ')[-1]
   target='피보험자가 보험기간 중 암보장개시일 이후 '+name.split('/ ')[-1]+'으로 진단확정되고 그 암의 직접적인 치료를 목적으로 항암약물치료 또는 항암방사선치료를 받은 경우.'
   amt=('계약 1년 미만에는 세부보장 가입금액의 50%, 1년 이후에는 100% 지급. 가입금액 100만원 기준 각각 50만원·100만원.' if kind<=3 else '해당 세부보장 가입금액의 100%. 가입금액 100만원 기준 100만원.')+' 실제 지급액은 해당 종의 계약 가입금액에 따라 계산합니다.'
   cond='세부보장(1~10종)별 최초 1회 지급. 계약일(부활일) 포함 90일 경과 다음 날부터 보장하며 갑상선암·기타피부암은 제외됩니다.'
 if '납입면제특약' in name or '납입면제5.10.5특약' in name:
  if di==3:
   diseases='암(갑상선암·기타피부암 제외)'
   if '3대질병' in name:diseases+='·뇌졸중·급성심근경색증'
   if '18대보장' in name:diseases='3대질병[암(갑상선암·기타피부암 제외)·뇌졸중·급성심근경색증], 10대질병[양성뇌종양·말기신부전증·말기간질환·말기폐질환·중증재생불량성빈혈·중증세균성수막염·루게릭병·다발경화증·질병으로 인한 실명·파킨슨병], 중대한 화상·부식의 진단 또는 관상동맥우회술·대동맥인조혈관치환수술·심장판막개심술 또는 희귀질환자 산정특례 신규등록'
   target='주계약 피보험자가 보험기간 중 보장개시 후 다음 사유에 해당한 경우: '+diseases+'.'
   cond='암은 계약일(부활일) 포함 90일 경과 다음 날부터 보장합니다. 약관에서 정한 면제대상 주계약·특약의 차회 이후 보험료를 면제합니다.'+(' 희귀질환자 산정특례 재등록은 제외합니다.' if '18대보장' in name else '')
  else:target='주계약 피보험자가 노인장기요양보험 등급판정위원회에서 장기요양 1~5등급으로 판정받은 경우. 만 65세 이상 또는 노인성 질병을 가진 만 65세 미만의 장기요양 대상자가 해당합니다.'
 # Retain only cash-benefit-specific limits where siblings have different scopes.
 if '급여항응고제처방급여금' in name:cond='와파린·NOAC 처방 각각 연간 1회 지급. 연간은 계약일부터 매 1년 단위로 계산합니다.'
 if '급여특정항혈소판제처방급여금' in name:cond='급여 특정 항혈소판제 처방에 대해 연간 1회 지급. 연간은 계약일부터 매 1년 단위로 계산합니다.'
 r['coverage_target']=norm(target);r['coverage_amount']=norm(amt);r['coverage_conditions']=norm(cond)
# Exact duplicate check, required fields and table-header contamination checks.
seen=set()
for i,r in enumerate(rows,1):
 r['id']=i
 key=(r['product_name'],r['coverage_name'],r['coverage_target'],r['coverage_amount'])
 assert key not in seen,key
 seen.add(key)
 assert '지급액: 지급금액' not in r['coverage_amount']
 assert '세부보장(종.' not in r['coverage_conditions']
 assert len(r['coverage_target'])>15 and len(r['coverage_amount'])>15
(R/'records.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
print('POLISHED',len(rows))


for r in rows:
 di=next(i for i in [1,3,5] if M[i]['path']==r['source_file']);pg=int(r['source_page'].split('–')[0]);name=r['coverage_name']
 for k in ['coverage_target','coverage_amount','coverage_conditions']:
  r[k]=r[k].replace('피 보험자','피보험자').replace('포 함','포함').replace('목 적','목적').replace('참 조','참조').replace('장기요 양','장기요양').replace('등급가','등급이').replace('중 증치매','중증치매').replace('보장 개시일','보장개시일')
 if '홈케어급여금' in name:
  r['coverage_target']='피보험자가 보험기간 중 보장개시 후 장기요양 1~3등급의 중등도이상 상태로 판정되고, 월계약해당일부터 다음 월계약해당일 전일까지 시설급여를 이용하지 않은 경우.'
  r['coverage_conditions']='계약일(부활일) 포함 90일 경과 다음 날부터 보장하며 재해가 직접 원인이면 계약일(부활일)부터 보장합니다. 해당 월 시설급여를 이용하지 않은 홈케어 발생에 대해 월 1회 지급합니다. 사망 다음 날부터 홈케어는 발생하지 않은 것으로 봅니다.'
 if di==5 and '중증이상장기요양' in name:
  r['coverage_target']=re.sub(r'경증이상장기요양상태\s*:\s*장기요양 1~5등급','',r['coverage_target']).strip()
 if di==5 and '생활자금' in name:
  waiting='치매: 계약일(부활일) 포함 1년 경과 다음 날부터 보장하며 재해로 인한 뇌 손상은 계약일(부활일)부터 보장합니다. ' if '중증치매간병' in name else '장기요양: 계약일(부활일) 포함 90일 경과 다음 날부터 보장하며 재해가 직접 원인이면 계약일(부활일)부터 보장합니다. '
  r['coverage_conditions']=waiting+'최초 36회를 보증지급합니다. 매년 최초 진단·판정 해당일에 생존하면 그해 12개월을 확정 지급하고, 보증기간 중 사망하면 잔여 보증금액을 지급합니다. 보험기간이 종료되어도 생존 요건을 충족하면 최대 종신 지급합니다.'
 if di==3 and pg in [662,672]:
  r['coverage_conditions']='계약일(부활일) 포함 90일 경과 다음 날부터 암을 보장합니다. 최초 진단일부터 10년간 진단일 기준 연간 1회 지급하며 10차년도 치료가 지급되면 해당 치료일까지로 지급기간이 종료됩니다. 계약 1년 미만 최초 진단의 50% 지급률은 전체 지급기간 동안 적용합니다. 전액본인부담·비급여 치료만 보장하고 급여 일부본인부담 치료는 제외합니다.'
 if di==5 and pg==195:
  r['coverage_target']='피보험자가 보험기간 중 시니어특정질환(약관 분류표의 치매·루게릭병·파킨슨병)으로 최초 진단확정된 경우.'
  r['coverage_conditions']='최초 1회 지급. 계약일(부활일) 포함 1년이 되는 날의 다음 날부터 보장하며 재해가 직접 원인이면 계약일(부활일)부터 보장합니다.'
 # Avoid repeating the same three treatment definitions.
 r['coverage_target']=re.sub(r'암 주요치료 : 암수술, 항암방사선치료, 항암약물치료 등\s*','',r['coverage_target'])
 # Remove duplicate annual-limit sentences when a concise limit is already present.
 if '연간 1회에 한함.' in r['coverage_conditions']:
  r['coverage_conditions']=re.sub(r'보험금의 지급횟수는[^.]*초과분[^.]*\.','',r['coverage_conditions'])
 r['coverage_conditions']=c(r['coverage_conditions'])
 # Record real PDF pages including body and payout notes.
 end=section(di,pg)[2]
 if '–' not in r['source_page']:r['source_page']=f"{r['section_start']}–{min(pg+2,end)}"
for r in rows:
 assert '해당 특약을 가입한 계약에 적용' not in r['coverage_conditions']
 assert '홈케어' not in r['coverage_name'] or '시설급여를 이용하지 않은' in r['coverage_target']
 assert not r['coverage_name'].endswith('세부보장(종)')
(R/'records.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
print('FINAL',len(rows),[(p,len([r for r in rows if r['product_name']==p])) for p in dict.fromkeys(r['product_name'] for r in rows)])

