import json,re
from pathlib import Path
def clean(t):return t.replace('\x00','').strip()
def comp(t):return re.sub(r'\s','',clean(t))
plans=[]
for d in range(4):
 pages=json.loads(Path(f'work/fast/p{d}.json').read_text(encoding='utf8'))
 sections=[]
 for i,t in enumerate(pages):
  lines=[clean(x) for x in t.splitlines() if clean(x)]
  if lines and (lines[0].startswith('무배당') or lines[0].startswith('선지급')) and '제1관' in comp('\n'.join(lines[:7])):
   title=' '.join(lines[:next((j for j,x in enumerate(lines) if '제1관' in comp(x)),1)])
   sections.append((i,title))
 records=[]
 for i,t in enumerate(pages):
  lines=[clean(x) for x in t.splitlines() if clean(x)]
  if not lines:continue
  header=comp('\n'.join(lines[:6]))
  if re.match(r'^[\[（(【]별표\d[\]）)】]',header) and '지급기준표' in header and ('지급사유' in comp(t) or '지급금액' in comp(t)):
   section=next(((s,title) for s,title in reversed(sections) if s<i),(-1,'주계약'))
   ends=i+1
   while ends<len(pages) and ends<i+15:
    nxt=clean(pages[ends]);nlines=[clean(x) for x in nxt.splitlines() if clean(x)]
    if not nlines:break
    if re.match(r'^[\[（(【]별표\d',comp(nlines[0])) or nlines[0].startswith('무배당') or ('분류표' in comp('\n'.join(nlines[:2])) and '지급기준표' not in comp('\n'.join(nlines[:2]))):break
    ends+=1
   records.append({'doc':d,'start':i+1,'end':ends,'section_start':section[0]+1,'section':section[1]})
 plans.extend(records)
 print(d,'sections',len(sections),'tables',len(records),'pages',sum(a['end']-a['start']+1 for a in records))
Path('work/table_plan.json').write_text(json.dumps(plans,ensure_ascii=False,indent=2),encoding='utf8')
