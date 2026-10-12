import json,re
from pathlib import Path
plans=json.loads(Path('work/table_plan.json').read_text(encoding='utf8'))
def c(t):return re.sub(r'\s','',t.replace('\x00',''))
for d in range(4):
 pages=json.loads(Path(f'work/fast/p{d}.json').read_text(encoding='utf8'))
 planned={n for a in plans if a['doc']==d for n in range(a['start'],a['end']+1)}
 unmatched=[];sections=[]
 for i,t in enumerate(pages):
  lines=[x.replace('\x00','').strip() for x in t.splitlines() if x.strip()]
  if not lines:continue
  if (lines[0].startswith('무배당') or lines[0].startswith('선지급')) and '제1관' in c('\n'.join(lines[:7])):
   title=' '.join(lines[:next((j for j,x in enumerate(lines) if '제1관' in c(x)),1)]);sections.append((i+1,title))
  if i+1 not in planned and '지급사유' in c(t) and '지급금액' in c(t) and '지급기준표' in c(t) and '별표' in c('\n'.join(lines[:4])):unmatched.append((i+1,t[:200]))
 missing=[]
 for j,(n,title) in enumerate(sections):
  end=sections[j+1][0] if j+1<len(sections) else len(pages)+1
  if not any(a['doc']==d and n<=a['start']<end for a in plans) and end-n>3:missing.append((n,end-1,title))
 print('DOC',d,'UNMATCHED',unmatched,'NO TABLE',missing)
