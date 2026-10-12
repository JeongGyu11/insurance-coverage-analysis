import json,re
from pathlib import Path
from datetime import datetime,timezone,timedelta
def compact(t):return re.sub(r'\s','',str(t or '').replace('\x00',''))
def tidy(t):return re.sub(r'[ \t]+',' ',str(t or '').replace('\x00','').replace('\n',' ')).strip()
def unpage(t):return re.sub(r'\n\d+\s*$','',t.replace('\x00',''))
def title_of(above):
 lines=above.replace('\x00','').splitlines();inds=[i for i,x in enumerate(lines) if re.match(r'^\s*(?:[■□●①-⑳]|\d+\.|[가-마]\.)',x)]
 if inds:
  title=tidy('\n'.join(lines[inds[-1]:]));title=re.sub(r'^[■□●①-⑳\s]+|^\d+\.\s*|^[가-마]\.\s*','',title)
 else:
  if any('종피보험자' in x and x.strip().startswith('-') for x in lines):return '생존연금(부부계약·종피보험자)'
  if any('주피보험자' in x and x.strip().startswith('-') for x in lines):return '생존연금(부부계약·주피보험자)'
  cand=[x for x in lines if re.search(r'\(제\s*\d+조',x)]
  title=tidy(cand[-1]) if cand else ''
 return re.sub(r'\s*\(제\s*\d+조.*','',title).strip()
plans=json.loads(Path('work/table_plan.json').read_text(encoding='utf8'))
pages=[json.loads(Path(f'work/fast/p{d}.json').read_text(encoding='utf8')) for d in range(4)]
counts=json.loads(Path('work/counts.json').read_text(encoding='utf8'))
products=['무배당 ABL우리들의달러연금보험','무배당 ABL THE톡톡튀는여성건강보험(해약환급금 미지급형)2506','무배당 ABL건강N더보장종합보험(갱신형)2501','무배당 ABL건강N더보장종합보험(해약환급금 미지급형)2504']
records=[];issues=[];table_stats=[]
now=datetime.now(timezone(timedelta(hours=9))).isoformat(timespec='seconds')
for plan in plans:
 d=plan['doc'];section=plan['section'].split('※')[0].strip();table_text='\n'.join(unpage(pages[d][n-1]) for n in range(plan['start'],plan['end']+1))
 basis=re.search(r'[\[(（]기준\s*[：:]([^\])）]+)[\])）]',table_text);basis=tidy(basis.group(1)) if basis else ''
 body='\n'.join(unpage(x) for x in pages[d][max(0,plan['section_start']-1):plan['start']-1])
 article_pat=r'(?m)^제\s*\d+조\s*[［\[]([^］\]]+)[］\]]'
 articles=[];matches=list(re.finditer(article_pat,body))
 for k,m in enumerate(matches):
  at=body[m.end():matches[k+1].start() if k+1<len(matches) else len(body)]
  if at.strip() and len(at.strip())>80:articles.append((compact(m.group(1)),tidy(at)))
 scope=next((t for name,t in articles if '피보험자의범위' in name),'피보험자')
 exclusion=next((t for name,t in articles if '보험금을지급하지않는사유' in name),'')
 notes=[]
 for n in range(plan['start'],plan['end']+1):
  txt=unpage(pages[d][n-1]);m=re.search(r'(?:\(주\)|㈜|（주）)',txt)
  if m:
   chunks=re.split(r'(?m)^(?=[■①-⑳]|\d+\.\s*[^\n]+\(제\s*\d+조|[가-마]\.\s*[^\n]*연금형)',txt[m.start():])
   for chunk in chunks:
    if re.match(r'^(?:\(주\)|㈜|（주）)',chunk):notes.append(tidy(chunk))
  elif notes and not ('지급사유' in compact(txt) or '지급금액' in compact(txt)):notes.append(tidy(txt))
 notes=' '.join(notes)
 # Table notes preserve limits, waiting periods, reduced benefits and premium waivers.
 definition_exclusions=[]
 for an,at in articles:
  if '정의및진단확정' in an and an!='용어의정의' and ('제외' in at or '보장하지' in at):
   for para in re.split(r'(?=[①-⑳])',at):
    if '제외합니다' in para or '보장하지 않습니다' in para:definition_exclusions.append(para)
 shared=' '.join(x for x in [notes,('보장범위 제외: '+' '.join(definition_exclusions)) if definition_exclusions else '',('보험금 지급 제외: '+exclusion) if exclusion else ''] if x)
 produced=0;pending=None
 for n in range(plan['start'],plan['end']+1):
  path=Path(f'work/cells/{d}_{n}.json')
  if not path.exists():continue
  pg=json.loads(path.read_text(encoding='utf8'))
  for ti,tab in enumerate(pg['tables']):
   # Nested tables are already present in the enclosing benefit cell.
   box=tab['bbox']
   if any(other is not tab and other['bbox'][0]<=box[0] and other['bbox'][1]<=box[1] and other['bbox'][2]>=box[2] and other['bbox'][3]>=box[3] and other['bbox']!=box for other in pg['tables']):continue
   rows=tab['rows'];allkeys=[compact(r[0]) for r in rows if r]
   if not any(compact(v) in ('지급사유','지급금액','지급액','지급보험금') for r in rows for v in r):
    # A page-break continuation may lack field labels.
    if pending and tab['bbox'][1]<140 and any(v and len(v)>15 for r in rows for v in r):
     if pending.get('_layout')=='horizontal':
      for rr in rows:
       cc=pending['_ci'];aa=pending['_ai']
       if len(rr)>cc and rr[cc]:pending['cause']+=' '+tidy(rr[cc])
       if len(rr)>aa:pending['amount']+=' '+' / '.join(tidy(v) for v in rr[aa:] if v)
     else:
      vals=[' / '.join(tidy(v) for v in r if v) for r in rows];pending['amount']+=' '+ ' '.join(vals)
     pending['page_end']=n
    continue
   heading=title_of(tab['above']);items=[];layout='vertical';ci=None;ai=None
   if any(k=='지급사유' for k in allkeys) and any(k in ('지급금액','지급액','지급보험금') for k in allkeys):
    cause=[];amount=[];mode='';carry=''
    for row in rows:
     key=compact(row[0]);vals=[tidy(v) for v in row[1:] if v]
     if key=='지급사유':mode='cause'
     elif key in ('지급금액','지급액','지급보험금'):mode='amount'
     elif key and mode=='amount':vals=[tidy(row[0])]+vals
     if mode=='cause':cause.extend(vals)
     elif mode=='amount':amount.append(' / '.join(vals))
    items=[{'name':heading,'cause':' '.join(cause),'amount':' ; '.join(amount)}]
   else:
    hi=next((k for k,r in enumerate(rows) if any(compact(v)=='지급사유' for v in r) and any(compact(v) in ('지급금액','지급액','지급보험금') for v in r)),None)
    if hi is not None:
     layout='horizontal'
     header=rows[hi];ci=next(i for i,v in enumerate(header) if compact(v)=='지급사유');ai=next(i for i,v in enumerate(header) if compact(v) in ('지급금액','지급액','지급보험금'))
     ni=next((i for i,v in enumerate(header) if compact(v) in ('명칭','급부명칭','구분','급여명칭','급부')),None)
     previous=None
     tiercarry={}
     for row in rows[hi+1:]:
      if len(row)<=max(ci,ai):continue
      cause=tidy(row[ci]);amount=' / '.join(tidy(v) for v in row[ai:] if v);name=tidy(row[ni]) if ni is not None else heading
      tier=[]
      for xi in range(ci+1,ai):
       if xi==ni:continue
       if row[xi]:tiercarry[xi]=tidy(row[xi])
       if xi in tiercarry:tier.append(tiercarry[xi])
      if ni is None:
       if previous is None:
        previous={'name':heading,'cause':'','amount':''};items.append(previous)
       if cause:previous['cause']+=('\n' if previous['cause'] else '')+cause
       if amount:previous['amount']+=('\n' if previous['amount'] else '')+((' '.join(tier)+'：') if tier else ((cause+'：') if cause else ''))+amount
      elif name and (cause or amount):
       name=re.sub(r'\s*\(제\s*\d+조.*','',name)
       item={'name':name,'cause':cause,'amount':amount};items.append(item);previous=item
      elif previous and (cause or amount):
       previous['cause']+=' '+cause;previous['amount']+=' ; '+amount
   for item in items:
    if not item['name'] or not item['amount'] or not item['cause']:
     issues.append({'doc':d,'page':n,'table':ti,'section':section,'reason':'담보명·금액·지급사유 연결 확인 필요','raw':tab});continue
    if len(item['name'])>180 or '지급사유' in item['name']:
     issues.append({'doc':d,'page':n,'table':ti,'section':section,'reason':'담보명 제목 확인 필요','raw':tab});continue
    localbasis=re.search(r'[\[(（]기준\s*[：:]([^\])）]+)[\])）]',tab['above'])
    rec={**item,'doc':d,'page':n,'page_end':n,'section':section,'product':products[d],'basis':tidy(localbasis.group(1)) if localbasis else basis,'target':scope,'conditions':item['cause']+('\n'+shared if shared else ''),'table_start':plan['start'],'_shared':shared,'_layout':layout,'_ci':ci,'_ai':ai}
    records.append(rec);pending=rec;produced+=1
   if not items and any('지급사유' in compact(v) for r in rows for v in r):
    issues.append({'doc':d,'page':n,'table':ti,'section':section,'reason':'비정형 지급기준표 확인 필요','raw':tab})
 table_stats.append({'doc':d,'start':plan['start'],'section':section,'rows':produced})
# Premium waiver benefits have no payment schedule and must be read from articles.
for d,pp in enumerate(pages):
 starts=[]
 for i,t in enumerate(pp):
  lines=[x.replace('\x00','').strip() for x in t.splitlines() if x.strip()]
  if lines and lines[0].startswith('무배당') and '보험료납입면제특약' in compact('\n'.join(lines[:4])) and '제1관' in compact('\n'.join(lines[:7])):
   title=' '.join(lines[:next((j for j,x in enumerate(lines) if '제1관' in compact(x)),1)])
   if '이특약은' in compact(t) or '이특약은' in compact(pp[i+1] if i+1<len(pp) else ''):starts.append((i,title))
 for s,section in starts:
  end=next((i for i in range(s+1,min(s+40,len(pp))) if re.match(r'^\s*[\[(（]별표',pp[i]) or pp[i].startswith('무배당')),min(s+30,len(pp)))
  body='\n'.join(unpage(x) for x in pp[s:end]);matches=list(re.finditer(article_pat,body));ars={}
  for k,m in enumerate(matches):ars[compact(m.group(1))]=tidy(body[m.end():matches[k+1].start() if k+1<len(matches) else len(body)])
  cause=ars.get('보험료납입면제사유','')
  if not cause:issues.append({'doc':d,'page':s+1,'section':section,'reason':'납입면제 사유 확인 필요','raw':{}});continue
  benefit=next((key for key in ['암','뇌출혈 및 뇌경색증','급성심근경색증'] if key in section),'선택질병')
  records.append({'name':benefit+' 보험료 납입면제','cause':cause,'amount':'납입면제 대상계약 및 이 특약의 차회 이후 보험료 납입 면제','doc':d,'page':s+1,'page_end':end,'section':section,'product':products[d],'basis':'','target':ars.get('피보험자의범위','피보험자'),'conditions':'\n'.join(v for key,v in ars.items() if '납입면제사유' in key or '납입면제에관한세부규정' in key or ('납입' in key and '않는사유' in key) or '납입면제대상계약' in key),'table_start':s+1})
# Contract termination on death also carries a contractual payment.
records.append({'name':'연금개시 전 사망 시 지급금','cause':'연금개시 전 보험기간 중 피보험자가 사망한 경우','amount':'사망 당시 계약자적립액과 이미 납입한 보험료 중 큰 금액을 계약자에게 지급','doc':0,'page':52,'page_end':52,'section':'무배당 ABL우리들의달러연금보험','product':products[0],'basis':'','target':'피보험자','conditions':'연금개시 전 보험기간 중 피보험자가 사망한 경우. 계약소멸에 따른 계약자 지급금으로 지급기준표 주석에 기재되어 있음.','table_start':52})
for r in records:
 if '_shared' in r:r['conditions']=r['cause']+('\n'+r['_shared'] if r['_shared'] else '')
 if r['doc']==0 and '_shared' in r:
  plan=next(a for a in plans if a['doc']==0 and a['start']==r['table_start'])
  src='\n'.join(unpage(pages[0][n-1]) for n in range(plan['start'],plan['end']+1))
  note_matches=list(re.finditer(r'(?:\(주\)|㈜|（주）)',src))
  tail=tidy(src[note_matches[-1].start():]) if note_matches else ''
  exclusions=r['_shared'].split('보험금 지급 제외: ',1)
  extra=('보험금 지급 제외: '+exclusions[1]) if len(exclusions)>1 else ''
  relevant=tail if ('연금' in r['name'] or r['name']=='노후설계자금') else ''
  r['conditions']='\n'.join(x for x in [r['cause'],relevant,extra] if x)
 if r['doc']==0 and r['section']=='무배당 ABL우리들의달러연금보험':
  r['basis']='통화: 미국 달러(USD)'
  if r['table_start']==55 and r['name']!='노후설계자금':r['name']+='(노후설계자금 선택 시)'
 if r['doc']==1 and r['section'].startswith('무배당 ABL') and r['target']=='피보험자':r['target']='여성 피보험자'
records.sort(key=lambda r:(r['doc'],r['page'],r.get('table_start',0)))
for i,r in enumerate(records,1):r['id']=i;r['created_at']=now;r['updated_at']=now
Path('work/records.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8')
Path('work/issues.json').write_text(json.dumps(issues,ensure_ascii=False,indent=2),encoding='utf8')
Path('work/table_stats.json').write_text(json.dumps(table_stats,ensure_ascii=False,indent=2),encoding='utf8')
print('records',len(records),'issues',len(issues),'zero tables',sum(s['rows']==0 for s in table_stats))
