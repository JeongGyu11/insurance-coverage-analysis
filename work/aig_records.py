import json,re
from pathlib import Path
from datetime import datetime,timezone,timedelta
out=Path('work/aig');benefits=json.loads((out/'benefits.json').read_text(encoding='utf8'));tabs=json.loads((out/'summary_tables.json').read_text(encoding='utf8'))
def tidy(s):return re.sub(r'\s+',' ',str(s or '').replace('\x00','')).strip()
def comp(s):return re.sub(r'\s','',str(s or '').replace('\x00',''))
def canon(s):
 s=comp(s);s=re.sub(r'^\d+(?:-\d+)?\.','',s).replace('[갱신형]','').replace('특별약관','')
 s=re.sub(r'\((?:305간편심사형|325간편심사형|간편심사)\)','',s)
 return s.replace('진단비','진단').replace('말기암호스피스통증완화치료비','말기암호스피스통증완화치료')
policies=[]
for d in range(3):
 p=json.loads((out/f'policy{d}.json').read_text(encoding='utf8'));flow=p['flow'];text='';offsets=[]
 for f in flow:offsets.append((len(text),f['page']));text+=f['text']+'\n'
 heads=list(re.finditer(r'(?m)^\d+(?:-\d+)?\.\s*\[갱신형\]',text));sections=[]
 for k,h in enumerate(heads):
  page=next(n for pos,n in reversed(offsets) if pos<=h.start())
  if page<30:continue
  stop=heads[k+1].start() if k+1<len(heads) else len(text)
  administrative=re.search(r'(?m)^제도성\s*특별약관|^2-1\.\s*자동갱신',text[h.start():stop])
  if administrative:stop=h.start()+administrative.start()
  chunk=text[h.start():stop]
  art=re.search(r'(?m)^제\s*1조\s*\(',chunk)
  if not art or art.start()>350:continue
  name=tidy(chunk[:art.start()]);articles={};ms=list(re.finditer(r'(?m)^제\s*\d+조\s*\(([^\n]+)\)\s*●?',chunk))
  for j,m in enumerate(ms):
   a=chunk[m.end():ms[j+1].start() if j+1<len(ms) else len(chunk)];articles[comp(m.group(1))]=tidy(a)
  sections.append({'name':name,'start':page,'end':next(n for pos,n in reversed(offsets) if pos<=stop-1),'articles':articles,'text':chunk})
 first=next((m.start() for m in heads if next(n for pos,n in reversed(offsets) if pos<=m.start())>=30),len(text))
 common='';general=text[:first];g=list(re.finditer(r'(?m)^제5조\s*\(보험금을 지급하지 않는 사유\)',general))
 if g:
  start=g[-1].end();end=re.search(r'(?m)^제6조\s*\(',general[start:]);common=tidy(general[start:start+end.start()] if end else '')
 policies.append({**p,'sections':sections,'common_exclusions':common})
 print('sections',d,len(sections))
records=[];issues=[];now=datetime.now(timezone(timedelta(hours=9))).isoformat(timespec='seconds').replace('T',' ')
for b in benefits:
 d=b['doc'];key=canon(b['name'])
 lookup=key
 if '전이암진단(' in key:lookup='전이암진단'
 candidates=[s for s in policies[d]['sections'] if canon(s['name'])==lookup]
 if not candidates:issues.append({'doc':d,'name':b['name'],'reason':'약관 제목 연결 확인 필요'});continue
 section=candidates[0];desc=tidy(b['description']);amount_parts=[]
 for pg in tabs:
  if pg['doc']!=d or pg['page']!=b['page']:continue
  for tab in pg['tables']:
   bbox=tab['bbox']
   if bbox[0]<196 or bbox[1]<b['bbox'][1]-1 or bbox[3]>b['bbox'][3]+1:continue
   rows=tab['rows'];hi=next((i for i,r in enumerate(rows) if any('지급금액'==comp(v) for v in r)),None)
   if hi is not None:
    for row in rows[hi+1:]:
     if len(row)>1:amount_parts.append('：'.join(tidy(v) for v in row if v))
 if amount_parts:amount='\n'.join(amount_parts)
 else:
  amount='보험증권에 기재된 해당 담보 보험가입금액(계약별 결정)'
  reduction=re.search(r'보험가입금액의(\d+(?:\.\d+)?%)',comp(desc))
  if reduction:
   period=re.search(r'(?:최초계약일|보험계약일|계약일).*?(\d+년)(?:미만|이내)',comp(desc))
   if period:amount+='; '+period.group(1)+' 미만 지급사유 발생 시 '+reduction.group(1)+' 지급'
  if '입원1일당' in comp(desc) or '1일당' in comp(b['name']):amount+=' (입원 1일당)'
  elif '통원1회당' in comp(desc):amount+=' (통원 1회당)'
 target='피보험자'
 if '간편' in b['product']:target+='(간편심사 대상; 세부 가입나이·보험기간은 사업방법서 및 계약별 기준)'
 conditions=[desc]
 if policies[d]['common_exclusions']:conditions.append('보통약관 공통 지급 제외: '+policies[d]['common_exclusions'])
 for name,txt in section['articles'].items():
  if '지급하지않는' in name or ('지급' in name and '세부규정' in name):
   # Keep benefit-specific rules; omit diagnostic disputes and claim-administration text.
   paras=re.split(r'(?=[①-⑳])',txt)
   chosen=[p for p in paras if len(p)>15 and any(w in comp(p) for w in ['보장개시일','50%','10%','5%','지급하지','제외','한도','차감','계속입원','면제','중복','상급종합병원','부활','재진단']) and not ('합의하지못할' in comp(p) or '제3자' in comp(p))]
   if chosen:conditions.append('약관 세부조건: '+' '.join(chosen))
   elif '지급하지않는' in name:conditions.append('약관 지급 제외: '+txt)
 official=b['name'] if '전이암진단(' in key else re.sub(r'^\d+(?:-\d+)?\.\s*','',section['name']).replace('특별약관','').strip()
 records.append({**b,'name':official,'amount':amount,'target':target,'conditions':'\n'.join(conditions),'policy_path':policies[d]['path'],'policy_start':section['start'],'policy_end':section['end'],'policy_name':section['name'],'created_at':now,'updated_at':now,'review':'담보명은 약관 제목 기준; 지급금액·조건은 상품요약서 및 해당 약관 조항 대조'})
for i,r in enumerate(records,1):r['id']=i
(out/'records.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8');(out/'issues.json').write_text(json.dumps(issues,ensure_ascii=False,indent=2),encoding='utf8')
(out/'sections.json').write_text(json.dumps([p['sections'] for p in policies],ensure_ascii=False,indent=2),encoding='utf8')
print('rows',len(records),'issues',issues)
