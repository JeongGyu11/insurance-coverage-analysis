from pathlib import Path
import json,re
from datetime import datetime,timezone,timedelta
p=Path('work/nh');m=json.loads((p/'manifest.json').read_text(encoding='utf8'));tabs=json.loads((p/'cells.json').read_text(encoding='utf8'));R=[];now=datetime.now(timezone(timedelta(hours=9))).isoformat(timespec='seconds').replace('T',' ')
def compact(t):return re.sub(r'\s','',t or '')
def clean(t):
 t=re.sub(r'(?m)^.*(?:주계약 약관|특약 약관)\s*\d+\s*$','',t)
 t=re.sub(r'(?m)^\d+\s+(?:온라인)?농업인NH안전보험.*$','',t)
 return re.sub(r'\s+',' ',t.replace('\x00',' ')).strip()
def pp(k):return json.loads((p/(k+'.json')).read_text(encoding='utf8'))
def articles(k,start,end):
 body='\n'.join(pp(k)[start-1:end]);ms=list(re.finditer(r'(?m)^제\s*(\d+)(?:조의\d+|조)【([^】]+)】',body));out={}
 for i,a in enumerate(ms):out[int(a.group(1))]=(a.group(2),body[a.end():ms[i+1].start() if i+1<len(ms) else len(body)])
 return out
def art(a,n):return clean(a.get(n,('',''))[1])
def sub(t,number):
 ms=list(re.finditer(r'(?m)^\(([1-4])\)\s*(?:상해|질병)(?:입원|통원)',t))
 for i,a in enumerate(ms):
  if int(a.group(1))==number:return clean(t[a.start():ms[i+1].start() if i+1<len(ms) else len(t)])
 return clean(t)
def add(k,form,name,amount,cond,page,bodypage,section='주계약',review=''):
 f=next(x for x in m if x['key']==k);prod='온라인농업인NH안전보험(무배당)' if k=='doc3' else '농업인NH안전보험(무배당)'
 target='농업경영체 등록 등 사업방법서의 자격요건을 충족한 농업·영농·산림 종사 피보험자. '+('온라인 가입 만 19세 이상; 일반 1형 87세, 산재형 84세까지.' if k=='doc3' else '일반형·휴일보장형 만 15~87세, 산재형 만 15~84세; 특약 만 15~87세.')
 R.append(dict(id=len(R)+1,company_name='NH농협생명',product_name=prod,coverage_name=name+' ['+form+' · '+section+']',coverage_target=target,coverage_amount=amount,coverage_conditions=cond,created_at=now,updated_at=now,type=form+' · '+section,source_file=f['path'],source_page=str(page),article_pages=str(bodypage),duplicate_paths=f['duplicate_paths'],table_notes='',review='2025년 7월 자료만 분석. '+review))
scope='농업작업안전재해는 약관의 농업작업 범위 중 발생한 재해분류표상 재해. 농업작업안전질병은 약관의 농업작업 관련 질병 분류표 대상 질병. 보험기간 1년, 평일·휴일 구분 없이 보장(휴일보장형 제외). '
medical=[
 ('상해입원',1,'하나의 농업작업안전재해당 5,000만원 한도. 입원실료·입원제비용·입원수술비 본인부담 의료비의 80%; 잔여 20%가 연간 200만원 초과 시 초과분 보상. 상급병실료 차액 50%, 1일 평균 10만원 한도.'),
 ('상해통원(외래·처방조제)',2,'외래 방문 1회당 20만원, 연간 180회; 처방전 1건당 10만원, 연간 180건. 외래 공제: 의원 등 1만원/병원 등 1.5만원/상급종합 등 2만원과 보상대상 의료비 20% 중 큰 금액. 처방조제 공제: 8천원과 보상대상 의료비 20% 중 큰 금액.'),
 ('질병입원',3,'하나의 농업작업안전질병당 5,000만원 한도. 입원실료·입원제비용·입원수술비 본인부담 의료비의 80%; 잔여 20%가 연간 200만원 초과 시 초과분 보상. 상급병실료 차액 50%, 1일 평균 10만원 한도.'),
 ('질병통원(외래·처방조제)',4,'외래 방문 1회당 20만원, 연간 180회; 처방전 1건당 10만원, 연간 180건. 외래 공제: 의원 등 1만원/병원 등 1.5만원/상급종합 등 2만원과 보상대상 의료비 20% 중 큰 금액. 처방조제 공제: 8천원과 보상대상 의료비 20% 중 큰 금액.'),
 ('비급여 도수치료·체외충격파치료·증식치료',56,'연간 350만원 및 각 치료횟수 합산 50회 한도. 1회당 2만원과 보상대상 의료비 30% 중 큰 금액 공제.'),
 ('비급여 주사료',61,'연간 250만원, 입원·통원 합산 50회 한도. 입원·통원 1회당 2만원과 보상대상 의료비 30% 중 큰 금액 공제.'),
 ('비급여 자기공명영상진단(MRI/MRA)',66,'연간 300만원 한도. 1회당 2만원과 보상대상 의료비 30% 중 큰 금액 공제.')]
for k in ['doc2','doc3']:
 online=k=='doc3';offset=5 if online else 0;aa=articles(k,24 if online else 29,101 if online else 106)
 for form,nums in [('일반 1형' if online else '일반형(1·2·3형)',[107,108]),('산재형',[109,110])]+([] if online else [('휴일보장형',[111,112])]):
  for n0 in nums:
   n=n0-offset;t=next(x for x in tabs if x['key']==k and x['page']==n);rows=t['tables'][0]['rows'];general=n0 in [107,108];skip=2 if general else 1
   for row in rows[skip:]:
    name=compact(row[0]);cause=clean(row[1] or '')
    if not cause or '상해·질병' in name:continue
    if general:
     ai=3 if n0==108 else 2;vals=row[ai:];carry='';vs=[]
     for val in vals:
      if val:carry=clean(val)
      vs.append(carry)
     amount=vs[0] if online else '; '.join(f'일반 {i+1}형: '+('보장하지 않음' if x=='-' else x) for i,x in enumerate(vs))
    else:amount=clean(row[-1])
    cond=scope+'\n'+cause+'\n보험금 지급 제외: '+art(aa,11)
    if '장해' in name or '간병' in name:cond+='\n'+art(aa,10)
    if '입원' in name:cond+='\n'+art(aa,7)+'\n'+art(aa,10)
    if '수술' in name:cond+='\n'+art(aa,5)+'\n'+art(aa,8)+'\n'+art(aa,10)
    if '감염병' in name:cond+='\n'+art(aa,6)
    if '휴일' in form:cond+='\n휴일은 약관 제2조 및 관련 정의 기준. SFTS 사망과 특정감염병 진단은 휴일 발생 여부로 제한하지 않음.'
    if not online and general and ('재해장해' in name):cond+='\n일반 3형에서는 이 담보를 보장하지 않음.'
    add(k,form,name,'[1구좌 기준] '+amount,cond,n,f'{29-offset}–{42-offset}',review='일반 1·2·3형 금액을 한 행에 구분 표기.' if general and not online else '')
  if form!='휴일보장형':
   for name,num,amount in medical:
    if num<5:cond=sub(aa[49][1],num)+'\n보상 제외: '+sub(aa[50][1],num)+'\n추가보장 관련: '+art(aa,51);pg=f'{72-offset}–{89-offset}'
    else:cond=art(aa,num)+'\n보상 제외: '+art(aa,num+1);pg=f'{90-offset if num==56 else 96-offset if num==61 else 102-offset}–{95-offset if num==56 else 101-offset if num==61 else 106-offset}'
    cond+='\n다수보험 처리: '+art(aa,52)
    add(k,form,'상해·질병치료급여금('+name+')',amount,'기본형 가입 시에만 보장; 상해·질병치료급여금 부(不)담보형은 보장하지 않음.\n'+scope+'\n'+cond,pg,pg,review='지급표의 상해·질병치료급여금을 특칙의 보장종목 7개로 분리. 부모 담보를 별도 행으로 중복 생성하지 않음.')
for n,start,section in [(132,123,'농업인장제비지원특약'),(144,134,'농업인재해사망특약'),(157,146,'농업인교통재해사망특약'),(170,159,'농업인재해골절특약'),(183,173,'농업인깁스치료특약')]:
 aa=articles('doc2',start,n-1);t=next(x for x in tabs if x['key']=='doc2' and x['page']==n)
 for ti,tab in enumerate(t['tables']):
  for row in tab['rows'][1:]:
   name=compact(row[0]);form='2종(휴일보장형)' if ti==1 else '1종(전일보장형)';amount=clean(row[2]);basis='보험가입금액 100만원 기준' if n==132 else '보험가입금액 10만원 기준' if n in [170,183] else '1구좌(보험가입금액 1,000만원) 기준'
   cond='특약 선택 가입 및 해당 보험료 납입 시 적용. '+('주계약 휴일보장형에만 부가 가능.' if ti==1 else '주계약 일반형 또는 산재형에만 부가 가능.')+'\n'+clean(row[1])
   for an,at in aa.values():
    if any(word in an for word in ['정의','세부규정','지급하지']):cond+='\n'+clean(at)
   if n==132:cond+='\n농협 조합원·비조합원 또는 농업경영체 영농 종사자의 사업방법서 자격요건에 한함(산림조합 자격만 충족하는 경우 제외).'
   add('doc2',form,name,'['+basis+'] '+amount,cond,n,f'{start}–{n-1}',section,'온라인 상품에는 종속특약 부가 불가.')
for x in R:
 assert len(x['coverage_conditions'])<32767,(x['coverage_name'],len(x['coverage_conditions']))
assert len(R)==83,(len(R),[(k,sum(x['product_name']==k for x in R)) for k in set(x['product_name'] for x in R)])
(p/'records.json').write_text(json.dumps(R,ensure_ascii=False,indent=2),encoding='utf8')
print('Rows',len(R),'offline',sum(x['product_name'].startswith('농업인') for x in R),'online',sum(x['product_name'].startswith('온라인') for x in R),'max conditions',max(len(x['coverage_conditions']) for x in R))
