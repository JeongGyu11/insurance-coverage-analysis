from pathlib import Path
import json,re,difflib
from datetime import datetime,timezone,timedelta
p=Path('work/nh_nonlife');B=json.loads((p/'benefits.json').read_text(encoding='utf8'));S=json.loads((p/'sections.json').read_text(encoding='utf8'));M=json.loads((p/'manifest.json').read_text(encoding='utf8'));I=json.loads((p/'inventory.json').read_text(encoding='utf8'));R=[];issues=[];now=datetime.now(timezone(timedelta(hours=9))).isoformat(timespec='seconds').replace('T',' ')
def comp(s):return re.sub(r'\s','',str(s or '').replace('\x00',''))
def tidy(s):return re.sub(r'\s+',' ',s or '').strip()
def canon(s):
 s=comp(s);s=re.sub(r'^\[\d종\]','',s);s=re.sub(r'^\d+(?:-\d+)?\.','',s);s=re.sub(r'※.*','',s)
 s=re.sub(r'^\[\d종(?:/\d종)?\]','',s);s=re.sub(r'^\d+(?:-\d+)?\.','',s)
 s=s.split(' - ')[0];s=re.sub(r'-\d+-.*','',s)
 s=s.replace('(갱신형)','').replace('갱신형','').replace('특별약관','').replace('보장','').replace('–','~').replace('-','~').replace('ㆍ','·').replace('․','·').replace('Ⅱ','II').replace('Ⅲ','III').replace('（','(').replace('）',')').replace('진단자금','진단비')
 s=re.sub(r'\([^()]+\)',lambda m:'('+''.join(sorted(m.group()[1:-1].split(',')))+')',s)
 return s
def pages(k):return json.loads((p/(k+'.json')).read_text(encoding='utf8'))
def sectionmatch(k,b):
 n=canon(b['name']);g=canon(b['group']);cand=[]
 for s in S[k]:
  if not s['articles']:continue
  sn=canon(s['name']);score=difflib.SequenceMatcher(None,n,sn).ratio()
  if k=='doc15' and n.startswith('유사암직접치료통원일당') and '요양병원제외' in n and s['name'].startswith('2-180.'):score=1
  if n==sn:score=1
  elif n in sn or sn in n:score=max(score,.90)
  if g and g==sn:score=1
  elif g and len(g)>5 and (g in sn or sn in g):score=max(score,.89)
  if n in ['교통상해후유장해(비운전자)(80%이상)','교통상해후유장해(비운전자)(80%미만)'] and set(re.findall(r'\([^()]+\)',n))==set(re.findall(r'\([^()]+\)',sn)) and sn.startswith('교통상해후유장해'):score=1
  cand.append((score,s))
 score,section=max(cand,key=lambda x:x[0]) if cand else (0,None)
 return section,score
def common(k):
 pp=pages(k);first=min((x['start'] for x in S[k] if x['articles']),default=len(pp));body='\n'.join(pp[:first-1]);ms=list(re.finditer(r'(?m)^제\s*\d+조\s*\((보험금을 지급하지 않는 사유)\)',body));res=''
 if ms:
  a=ms[-1];end=re.search(r'(?m)^제\s*\d+조\s*\(',body[a.end():]);res=tidy(body[a.end():a.end()+end.start()] if end else body[a.end():])
 return res
C={k:common(k) for k in S}
def policyfile(k,folder):
 f=next(x for x in I if x['kind']=='약관' and x['product_folder']==folder);return f['path']
def prodname(folder):return folder.split('_',3)[-1].replace('_',' ').replace('(무) ','무배당 ')
folders=sorted(set(x['product_folder'] for x in I))
def eligible(folder,b):
 n=comp(b['name'])
 if b['key']=='doc1':return '다이렉트암' in folder and (('갱신형' in n)==('종합형' in folder))
 if b['key']=='doc5':
  if '헤아림상해치료' not in folder:return False
  simple='320' in folder
  if '교통상해사망' in n:return simple==(b['page']==9)
  return simple==('320' in n or '320' in comp(b['group']))
 if b['key']=='doc8':
  if '펫앤미' not in folder:return False
  dog='강아지' in folder;lean='실속형' in folder
  if '일반상해후유장해' in n:return b['page']==6 if dog and lean else b['page']==7 if dog else b['page']==8
  if '위탁비용' in n:return not lean and ((dog and b['page']==8) or (not dog and b['page']==9))
  if '강아지' in n and not dog or '고양이' in n and dog:return False
  if '실속형' in n:return lean
  if '일반형' in n:return not lean
  return True
 if b['key']=='doc11':return 'MBTI' in folder
 if b['key']=='doc14':
  if '아이맘' not in folder:return False
  if '2종(표준형)에한함' in n and '1종' in folder:return False
  return True
 return False
for folder in folders:
 prod=prodname(folder)
 for b0 in B:
  if not eligible(folder,b0):continue
  b=dict(b0)
  if b['key']=='doc14' and b['name'] in ['팔꿈치, 손목, 발목','어깨,무릎','고관절']:b['name']='주요관절손상수술치료비(급여,연간1회한)('+b['name']+')';b['group']='주요관절손상수술치료비(급여)(연간1회한)'
  if b['key']=='doc14' and b['name'].startswith('1일당 7만원'):b['cause']+='\n간병인 실제 사용비용 구분: '+b['name'];b['name']=b['group']
  if b['key']=='doc14' and '어린이심장' in b['name'] and '시술비' in b['name']:b['name']='어린이심장개흉수술및특정시술비'
  if b['key']=='doc14' and b['name']=='특정 선천이상 다발성 선천이상':b['name']='선천이상수술비Ⅱ(특정선천이상·다발성선천이상)'
  if b['key']=='doc14' and b['name']=='상급종합 병원 상급종합 병원 제외':b['cause']+='\n세부보장 구분: '+b['name'];b['name']='임신출산질환(유산제외)통원일당(10회한)'
  if b['key']=='doc14' and b['name']=='산후우울증진단비':b['name']='산후우울증치료비'
  k={'doc1':'doc3' if '종합형' in folder else 'doc2','doc5':'doc6','doc8':'doc9','doc11':'doc12','doc14':'doc15'}[b['key']]
  section,score=sectionmatch(k,b);base=('교통상해사망' in b['name'] and b['key']=='doc5') or ('일반상해후유장해' in b['name'] and b['key']=='doc8') or (b['key']=='doc14' and b['page']==47 and b['table']==0) or (b['key']=='doc1' and '갱신형암진단비(유사암제외)'==comp(b['name'])) or (b['key']=='doc11' and '대중교통이용중' in b['name'])
  name=tidy(b['name']);conditions=[b['cause']];amount=b['amount'].replace('가입금액','보험증권에 기재된 해당 보장 보험가입금액')
  if section and score>=.73 and not base:
   policy_start,policy_end=section['start'],section['end'];source_name=section['name']
   for a in section['articles']:
    an=comp(a['title'])
    if any(x in an for x in ['지급사유','보상하는손해','손해의보상','지급하지않는','보상하지않는','세부규정','보장개시','보상한도','자기부담','정의','보장별보험금']):conditions.append('약관 '+a['title']+': '+a['text'])
  else:
   policy_start=1;policy_end=min(x['start'] for x in S[k] if x['articles'])-1;source_name='보통약관'
   if not base:issues.append(dict(product=prod,name=name,score=round(score,3),candidate=section['name'] if section else '',key=k,summary_page=b['page']))
  if base:
   payranges={'doc3':(66,107),'doc6':(62,104),'doc9':(67,107),'doc15':(108,124),'doc12':(3,6)}
   ps,pe=payranges[k];body='\n'.join(pages(k)[ps-1:pe-1]);ams=list(re.finditer(r'(?m)^제\s*\d+조\s*\(([^\n]+)\)',body))
   for ai,am in enumerate(ams):
    if any(x in comp(am.group(1)) for x in ['지급사유','세부규정','지급하지않는','보상하는손해']):conditions.append('기본계약 '+tidy(am.group(1))+': '+tidy(body[am.end():ams[ai+1].start() if ai+1<len(ams) else len(body)]))
   policy_start,policy_end=ps,pe-1
  if C[k]:conditions.append('보통약관 공통 지급 제외: '+C[k])
  target='피보험자(세부 가입나이·보험기간·인수기준은 사업방법서 및 계약별 기준)'
  if b['key']=='doc8':
   if '반려동물' in name:target='보험증권에 기재된 '+('강아지' if '강아지' in folder else '고양이')+' 및 반려인; 반려동물 관련 국내 거주·가입나이·건강상태 등 약관 기준 적용'
   if '치료비' in name:conditions.append('반려동물 치료비 및 확장보장: 보험증권의 자기부담금을 차감한 뒤 보상비율 적용. 질병 보장개시일은 최초계약일부터 30일이 지난 다음날이며 상해는 최초계약일. 확장보장은 기본 치료비와 합산하여 해당 치료비 보상한도 내 지급. 세부 면책·제외는 연결된 약관 기준.')
  if b['key']=='doc14' and any(x in comp(name) for x in ['모성','임신','산모','유산','태반','산후','양수','분만','여성산과','출산전']):target='약관에서 정한 부양자·산모 또는 피보험자(해당 특약의 피보험자 범위에 따름)'
  review='담보별 상품요약서의 지급사유·금액과 약관 조항 연결. '
  if 'NH펫앤미든든보험[3종' in folder:review+='고양이 폴더 사업방법서·상품요약서 파일명 교차: 내용 기준으로 원문 식별. '
  review+=('보통약관 기본 보장.' if base else '약관 제목 연결 확인 필요.' if score<.73 else '관련 특별약관 연결.')
  if b0['name']=='산후우울증진단비':review+=' 상품요약서 담보명은 진단비로 표시되나 약관명 치료비를 우선 기록.'
  name=comp(name)
  if b['key']=='doc14' and '간병인사용' in name and '요양병원제외' in name:amount='간병인 사용일 1일당: 사용금액 7만원 이상이면 해당 특약 보험가입금액의 100%, 7만원 미만이면 50%; 1회 입원당 180일 한도'
  if b['key']=='doc11' and '대중교통이용중' in name:amount='사망: 보험증권의 보험가입금액; 후유장해: 보험가입금액 × 장해분류표의 해당 지급률'
  cond='\n'.join(dict.fromkeys(tidy(x) for x in conditions if x))
  if len(cond)>32767:raise ValueError((prod,name,len(cond)))
  if any(x['product_name']==prod and comp(x['coverage_name'])==comp(name) for x in R):continue
  R.append(dict(id=len(R)+1,company_name='NH농협손해보험',product_name=prod,coverage_name=name,coverage_target=target,coverage_amount=amount,coverage_conditions=cond,created_at=now,updated_at=now,type='기본계약' if base else '선택계약',source_file=policyfile(k,folder),source_page=f'{policy_start}–{policy_end}',article_pages=f'{policy_start}–{policy_end}',summary_file=next(x['path'] for x in M if x['key']==b['key']),summary_page=str(b['page']) if b['end_page']==b['page'] else f"{b['page']}–{b['end_page']}",source_name=source_name,review=review,match_score=score,raw=b))
(p/'records.json').write_text(json.dumps(R,ensure_ascii=False,indent=2),encoding='utf8');(p/'link_issues.json').write_text(json.dumps(issues,ensure_ascii=False,indent=2),encoding='utf8');print('Rows',len(R),'issues',len(issues),'max condition',max(len(x['coverage_conditions']) for x in R));print([(n,sum(x['product_name']==n for x in R)) for n in dict.fromkeys(x['product_name'] for x in R)]);print(issues[:30])
