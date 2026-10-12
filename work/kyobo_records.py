from pathlib import Path
import json,re
from datetime import datetime,timezone,timedelta
p=Path('work/kyobo');m=json.loads((p/'manifest.json').read_text(encoding='utf8'));ss=json.loads((p/'sections.json').read_text(encoding='utf8'));tabs=json.loads((p/'tables.json').read_text(encoding='utf8'));records=[];issues=[]
now=datetime.now(timezone(timedelta(hours=9))).isoformat(sep=' ',timespec='seconds')
def clean(t):return re.sub(r'\s+',' ',t or '').strip()
def compact(t):return re.sub(r'\s+','',t or '')
def benefit(t):return re.sub(r'\((?:약관)?제\d+조[^)]*\)','',compact(t)).strip('“”')
def add(f,s,n,name,cause,amount,notes,context=''):
 product=re.sub(r'^판매(?:완료|중)__\d+_','',f['product_folder']).replace('_',' ').replace('(무)','무배당 ')
 rider=clean(s['name']);rider=re.sub(r'\s+','',rider).replace('약관주계약주계약(적립형)￡','')
 if '주계약' in rider:
  if '적립형' in rider and '보장형' not in rider:rider='주계약(적립형 전환계약)'
  else:rider='주계약'
 if '일반종신전환형' in amount:rider='주계약(일반종신전환형 전환계약)'
 if '생활자금전환계약' in compact(amount):rider='주계약(생활자금 전환계약)'
 cname=benefit(name);full=cname if compact(product)==rider else rider+' / '+cname
 condparts=[clean(cause)]
 for a in s['articles']:
  if (a['title'] in ['보험금의 지급사유','보험금 지급에 관한 세부규정','보험금을 지급하지 않는 사유','보험료 납입면제 사유','보험료 납입면제에 관한 세부규정','보험료 납입면제']) or ('보장개시' in a['title']) or ('정의' in a['title'] and len(clean(a['text']))<4500):
   text=a['text'];text=re.split(r'\(\s*별표\s*\d+\s*\)',text)[0];condparts.append(clean(text))
 condparts.append(clean(notes));cond='\n'.join(dict.fromkeys(x for x in condparts if x))
 if len(cond)>31000:issues.append(['long',f['key'],n,cname,len(cond)])
 r=dict(id=0,company_name='교보생명',product_name=product,coverage_name=full,coverage_target='해당 주계약·특약의 피보험자(가입나이·보험기간·인수기준은 사업방법서 및 계약별 기준)',coverage_amount=(context+' '+clean(amount)).strip(),coverage_conditions=cond,created_at=now,updated_at=now,source_file=f['path'],source_page=str(n),article_pages=f"{s['start']}–{s['end']}",source_name=rider,review='상품요약서 미제공: 약관 지급표·관련 조항 기준. 선택특약/전환계약은 해당 계약 부가·전환 시 적용.',type='주계약' if '주계약' in rider else '특약')
 found=next((x for x in records if x['product_name']==product and x['coverage_name']==full),None)
 if found:
  if r['coverage_amount'] not in found['coverage_amount']:found['coverage_amount']+='\n'+r['coverage_amount']
  if clean(cause) and clean(cause) not in found['coverage_conditions']:found['coverage_conditions']+='\n'+clean(cause)
  if str(n) not in found['source_page'].split(', '):found['source_page']+=', '+str(n)
 else:records.append(r)

for f in m:
 if f['kind']!='약관':continue
 a=json.loads((p/(f['key']+'.json')).read_text(encoding='utf8'));last=None
 for x in sorted((x for x in tabs if x['key']==f['key']),key=lambda x:x['page']):
  n=x['page'];s=next((s for s in ss[f['key']] if s['start']<=n<=s['end']),None)
  if not s:continue
  for ti,t in enumerate(x['tables']):
   if not t['fixed']:continue
   text=a[n-1];basis=re.findall(r'\([^\n]*기\s*준[^\n]*\)',t['above']);context=(' '.join(dict.fromkeys(clean(z) for z in basis)))
   if not context:
    for prev in range(n-1,max(s['start']-2,n-6),-1):
     bs=re.findall(r'\([^\n]*기\s*준[^\n]*\)',a[prev])
     if bs:context=clean(bs[-1]);break
   labels=re.findall(r'\[([^\]\n]+)\]',t['above']);context+=(' ['+labels[-1]+']') if labels and any(z in labels[-1] for z in ['계약','형','지급']) else ''
   end=n
   while end<len(a) and end<n+5 and end<s['end'] and not re.search(r'보험금을\s*지급할\s*때의\s*적립이율|재해분류표|질병분류표|연금지급\s*기준표',a[end]):end+=1
   notes='\n'.join(a[n-1:end]);notes=notes[notes.find('(주)'):] if '(주)' in notes else notes[notes.find('주)'):] if '주)' in notes else ''
   for row in t['fixed']:
    if len(row)==2:
     cause,amount=row;name='장기요양연금' if '장기요양상태' in cause else '생존연금'
    else:name,cause,amount=row
    name=benefit(name)
    if not name or name.startswith('(제'):
     if last and last[0]==s['start']:
      name=last[1]
     else:issues.append(['empty_name',f['key'],n,row]);continue
    if not amount and last and last==(s['start'],name):
     rec=next((z for z in reversed(records) if z['source_name']==compact(s['name']) and z['coverage_name'].endswith(name)),None)
     if rec:rec['coverage_conditions']+='\n[다음 페이지에서 이어지는 지급사유] '+clean(cause);rec['source_page']+=', '+str(n);continue
    if not cause or not amount:issues.append(['missing',f['key'],n,name,row])
    add(f,s,n,name,cause,amount,notes,context);last=(s['start'],name)
# The PDF has several borderless benefit tables. Link them to their explicit clauses.
for f in m:
 if f['kind']!='약관':continue
 for s in ss[f['key']]:
  title=s['name'];pay=next((a['text'] for a in s['articles'] if a['title'] in ['보험료 납입면제 사유','보험료 납입면제','보험금의 지급사유']),None)
  if '재해장해연금특약' in title:
   a=json.loads((p/(f['key']+'.json')).read_text(encoding='utf8'))
   for threshold in ['80% 이상','50% 이상']:
    add(f,s,1604,'재해장해연금('+threshold+')','보험기간 중 동일한 재해의 여러 신체부위 장해지급률 합계 '+threshold+'; 각 최초 1회.','매년 특약보험가입금액의 15% × 10회(확정지급); 가입금액 1,000만원 기준 매년 150만원, 총 1,500만원',a[1603])
  elif '납입면제' in title and pay:
   if '특정3대질환' in title:
    kinds=re.findall(r'[①②③④⑤]\s*(\d형\([^\n]+\))',pay)
    for kind in kinds:add(f,s,s['start'], '보험료납입면제 '+kind,'이 행은 '+kind+'에 적용.\n'+pay,'해당 형태의 납입면제 대상계약 차회 이후 보험료 납입 면제(현금 보험금 아님)','다른 형태의 조항은 공통 약관 대조용이며, 해당 행의 형별 사유·대상계약만 적용.')
   else:add(f,s,s['start'],'보험료납입면제',pay,'주계약·해당 특약의 차회 이후 보험료 납입 면제'+(' (12개월분 한도)' if '서비스' in title else ''),'')
  elif '선지급' in title and pay:
   amount='주계약 사망보험금의 50% 이내에서 신청한 금액; 최초 1회' if '장기간병' in title else '주계약 사망보험금 일부 또는 전부에서 약관의 할인금액·대출원리금 등을 차감한 선지급 금액'
   add(f,s,s['start'],'장기간병보험금(선지급)' if '장기간병' in title else '사망보험금(선지급)',pay,amount,'기존 사망보험금의 선지급 제도이며 별도의 추가 사망보험금이 아님.\n'+'\n'.join(a['text'] for a in s['articles'] if '세부' in a['title']))
  elif '사후정리' in title and pay:add(f,s,s['start'],'사후정리보험금',pay,'주계약 및 특약 사망보험금(재해사망 제외)의 일부 또는 전부; 해당 수익자의 지급비율·약관 한도 내','기존 사망보험금의 지급 제도이며 추가 사망보험금이 아님.')
  elif '양육연금' in title:
   body='\n'.join(a['text'] for a in s['articles'] if a['title'] in ['양육연금의 운용에 관한 사항','양육연금지급서비스특약의 신청에 관한 사항','양육연금을 받는 자의 범위 및 자격의 득실'])
   add(f,s,s['start'],'양육연금',body,'가입자녀에게 지급되는 주계약 사망보험금의 50% 이상 선택한 기준금액을 종료나이(15·20·25세)까지 분할 지급; 나중 지급 금액은 평균공시이율 연복리 가산','기존 사망보험금의 분할지급 제도이며 추가 사망보험금이 아님.');records[-1]['coverage_target']='주계약 피보험자의 가족관계등록부상 또는 주민등록상 자녀(가입자녀)'
# Name cleanup for narrow merged label columns; their full payment clauses remain recorded.
for r in records:
 rider,name=r['coverage_name'].split(' / ',1) if ' / ' in r['coverage_name'] else ('',r['coverage_name'])
 if '급여수술(기본)' in rider:name='통원(당일입원포함)급여수술보험금' if '통원' in name else '입원(당일입원제외)급여수술보험금'
 if '급여수술(방법)' in rider:
  match=re.search(r'주요급여수술[1-4]',name)
  if match:name=match.group()+'보험금'
 if '급여수술(원인)' in rider and '뇌질환' in name:name='뇌질환및심장질환급여수술보험금'
 if '연금전환특약' in rider:
  if '개인' in name:name='생존연금(종신연금형·개인형)'
  elif '주피' in name:name='생존연금(종신연금형·부부형·주피보험자연금)'
  elif '배우자' in name:name='생존연금(종신연금형·부부형·배우자연금)'
  elif '확정' in name:name='생존연금(확정기간연금형)'
  elif '상속' in name:name='생존연금(상속연금형)'
 r['coverage_name']=rider+' / '+name if rider else name
 if r['coverage_name']=='주계약 / 사망보험금':
  if '밸류업' in r['product_name']:
   r['coverage_amount']+='; 기본사망보험금: 보험가입금액 100%에서 1년 경과 연계약해당일부터 매년 직전 기본사망보험금의 10% 정률 체증(20년 경과 연계약해당일 전일까지, 총 19회 체증 후 유지); 추가계약자적립액 및 약관상 유지보너스 적립액 함께 지급'
  elif '경영인' in r['product_name']:
   r['coverage_amount']+='; 기본사망보험금과 이미 납입한 보험료 중 큰 금액. 기본사망보험금은 보험가입금액 100%에서 10년 경과 후 매년 가입금액의 5% 또는 10% 정액 체증(선택 플랜; 40년 경과 연계약해당일까지, 90세 계약해당일 제외)'
for i,r in enumerate(records,1):r['id']=i
(p/'records.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8');(p/'issues.json').write_text(json.dumps(issues,ensure_ascii=False,indent=2),encoding='utf8')
print('rows',len(records),'issues',len(issues));print('\n'.join(str(x) for x in issues));print('counts',[(n,sum(x['product_name']==n for x in records)) for n in dict.fromkeys(x['product_name'] for x in records)])
