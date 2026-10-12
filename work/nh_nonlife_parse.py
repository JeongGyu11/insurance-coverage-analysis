from pathlib import Path
import re,json
p=Path('work/nh_nonlife');tabs=json.loads((p/'tables.json').read_text(encoding='utf8'));manifest=json.loads((p/'manifest.json').read_text(encoding='utf8'))
def comp(s):return re.sub(r'\s','',str(s or '').replace('\x00',''))
def tidy(s):return re.sub(r'\s+',' ',str(s or '').replace('\x00',' ')).strip()
B=[];issues=[];last_by_slot={}
for pg in tabs:
 for ti,t in enumerate(pg['tables']):
  slot=(pg['key'],round(t['bbox'][0]/150));prev=last_by_slot.get(slot)
  rows=t['rows'];hi=next((i for i,row in enumerate(rows) if any(comp(v)=='지급사유' for v in row) and any(comp(v)=='지급금액' for v in row)),None)
  if hi is None:continue
  header=rows[hi];ci=next(i for i,v in enumerate(header) if comp(v)=='지급사유');ai=next(i for i,v in enumerate(header) if comp(v)=='지급금액')
  parent='';amountcarry=''
  for ri,row in enumerate(rows[hi+1:],hi+1):
   if len(row)<=ai:issues.append([pg['key'],pg['page'],ti,ri,'short']);continue
   left=[tidy(v) for v in row[:ci]];cause=tidy(row[ci]);amount=tidy(row[ai]);leaf=next((v for v in reversed(left) if v),'')
   if left and left[0]:parent=left[0]
   if ci>1 and any(left[1:]):name=leaf;group=parent
   else:name=leaf;group=''
   if not name and (cause or amount):
    if prev:
     prev['cause']+='\n'+cause;prev['amount']+='\n'+amount;prev['end_page']=pg['page']
    else:issues.append([pg['key'],pg['page'],ti,ri,'continuation without previous'])
    continue
   if not name:continue
   if ri==hi+1 and name.startswith('~') and prev:
    prev['name']+=name;prev['cause']+=' '+cause;prev['amount']+=' '+amount;prev['end_page']=pg['page'];continue
   if ri==hi+1 and not row[ai] and cause and prev and pg['page']>prev['page']:
    prev['name']+=name;prev['cause']+=' '+cause;prev['end_page']=pg['page'];continue
   if not amount:amount=amountcarry
   else:amountcarry=amount
   if not cause:
    if prev and ('1일당' in name):prev['cause']+='\n세부 지급 구분: '+name;continue
    if prev and name.startswith('비('):prev['name']+=name;prev['amount']+=' '+amount;prev['end_page']=pg['page'];continue
    if not row[ai]:
     b=dict(key=pg['key'],page=pg['page'],end_page=pg['page'],name=name,group=group,cause='',amount='',bbox=t['bbox'],above=t['above'],table=ti,row=ri);B.append(b);prev=b;last_by_slot[slot]=b;continue
    issues.append([pg['key'],pg['page'],ti,ri,'missing cause',name]);continue
   # A merged driver/non-driver base benefit is two distinct insured contexts.
   names=[name]
   if '교통상해사망(운전자)' in comp(name) and '교통상해사망(비운전자)' in comp(name):names=['교통상해사망(운전자)','교통상해사망(비운전자)']
   for nm in names:
    b=dict(key=pg['key'],page=pg['page'],end_page=pg['page'],name=nm,group=group,cause=cause,amount=amount,bbox=t['bbox'],above=t['above'],table=ti,row=ri)
    if len(names)==2:b['cause']='교통상해로 사망시' if nm=='교통상해사망(운전자)' else '비운전중 교통상해로 사망시'
    B.append(b);prev=b;last_by_slot[slot]=b
# Remove a page-end enclosing heading when the next page lists its payable sub-benefit.
B=[b for b in B if b['cause'] or b['amount']]
expanded=[]
for b in B:
 if b['key']=='doc14' and '통합화상진' in b['name'] and all(v in comp(b['name']) for v in ['1도이상','2도이상','3도이상']):
  for n in [1,2,3]:expanded.append({**b,'name':f'통합화상진단비({n}도이상)','cause':f'상해의 직접적인 결과로써 {n}도화상으로 진단 확정된 경우','amount':'(1사고당) 보험증권에 기재된 해당 세부보장 가입금액'})
 elif b['key']=='doc14' and '144대' in b['name']:
  for disease in ['27대질병','11대질병','59대생활질환','43대생활질환','다빈도4대질병']:expanded.append({**b,'name':'144대질병수술비('+disease+')','group':'144대질병수술비','cause':disease+'으로 진단확정 후 수술을 받은 경우','amount':'(수술1회당) 보험증권에 기재된 해당 세부보장 가입금액'})
 elif b['key']=='doc14' and '13대특정암' in b['name'] and '중증질환자' in b['group']:expanded.append({**b,'name':b['group'],'cause':b['cause']+'\n세부보장 구분: '+b['name']})
 else:expanded.append(b)
B=expanded
# MBTI summary separates payment triggers from example premiums; benefit amounts are policy-defined.
mb=next(x for x in tabs if x['key']=='doc11' and x['page']==2)['tables'][0]['rows']
for row in mb[1:]:B.append(dict(key='doc11',page=2,end_page=2,name=tidy(row[1]),group='',cause=tidy(row[2]),amount='보험증권에 기재된 해당 보장의 보험가입금액 또는 약관의 손해액 산식(계약별 결정)',bbox=[],above='',table=0,row=0))
(p/'benefits.json').write_text(json.dumps(B,ensure_ascii=False,indent=2),encoding='utf8');(p/'parse_issues.json').write_text(json.dumps(issues,ensure_ascii=False),encoding='utf8')
print('Benefits',len(B),'by summary',[(k,sum(b['key']==k for b in B)) for k in ['doc1','doc5','doc8','doc11','doc14']],'issues',issues)
# Policy section headers are used for exact source linkage and benefit-specific rules.
sections={}
for k in ['doc2','doc3','doc6','doc9','doc12','doc15']:
 pages=json.loads((p/(k+'.json')).read_text(encoding='utf8'));flow='';offsets=[]
 for n,t in enumerate(pages,1):offsets.append((len(flow),n));flow+=t+'\n'
 def pageat(pos):return next(n for start,n in reversed(offsets) if start<=pos)
 pat=r'(?m)^(?:\[\d종(?:/\d종)?\]\s*)?\d+(?:-\d+)?\.[^\n]{2,110}' if k!='doc12' else r'(?m)^[^\n]{2,110} 특별약관\s*$'
 hs=[]
 for a in re.finditer(pat,flow):
  title=tidy(a.group());after=flow[a.end():a.end()+4000]
  if ('무배당' in title and ('▶' in title or '◀' in title)) or title in ['특별약관','Ⅰ. 상해관련 특별약관','Ⅱ. 질병관련 특별약관']:continue
  firstarticle=re.search(r'(?m)^제\s*1조\s*\(',after)
  if not firstarticle or firstarticle.start()>3500:continue
  before=after[:firstarticle.start()]
  if re.search(r'(?m)^제\s*[2-9]\d*조',before):continue
  if not any(x in title+before[:250] for x in ['보장','약관','일반조항','반려동물']):continue
  if '···' in title or '…' in title:continue
  if pageat(a.start())<{'doc15':100,'doc2':95,'doc3':107,'doc6':104,'doc9':107,'doc12':20}[k]:continue
  hs.append(a)
 ss=[]
 for i,a in enumerate(hs):
  end=hs[i+1].start() if i+1<len(hs) else len(flow);body=flow[a.end():end];ams=list(re.finditer(r'(?m)^제\s*(\d+)(?:조의\d+|조)\s*\(([^\n]+)\)',body));ars=[]
  for j,am in enumerate(ams):ars.append(dict(number=int(am.group(1)),title=tidy(am.group(2)),text=tidy(body[am.end():ams[j+1].start() if j+1<len(ams) else len(body)])))
  lead=body[:ams[0].start()] if ams else ''
  title=tidy(a.group()+' '+lead.split('※')[0]);title=re.sub(r'▶.*|◀.*','',title).strip()
  ss.append(dict(name=title,start=pageat(a.start()),end=pageat(end-1),articles=ars))
 for si,s in enumerate(ss):
  if not s['articles'] and si+1<len(ss):s['articles']=ss[si+1]['articles'];s['end']=ss[si+1]['end']
 sections[k]=ss;print(k,'sections',len(ss),[x['name'] for x in ss[:3]])
(p/'sections.json').write_text(json.dumps(sections,ensure_ascii=False,indent=2),encoding='utf8')
