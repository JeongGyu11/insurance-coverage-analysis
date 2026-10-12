import json,re
from pathlib import Path
R=Path('work/heungkuk');S=json.loads((R/'sections.json').read_text(encoding='utf8'))
def co(s):return re.sub(r'\s+','',s or '')
for k,secs in S.items():
 p=json.loads((R/f'doc{k}.json').read_text(encoding='utf8'));toc='\n'.join(p[:70]).replace('\r','');entries=[]
 for z in re.finditer(r'(?m)^\s*\d+(?:-\d+)*\.\s*([^\n]*?)\s*특별약관\s*[·. …]+\s*(\d+)\s*$',toc):
  n=co(z[1]);page=int(z[2])
  if 1<=page<=len(p):entries.append((page,n))
 boundaries=sorted(set(x[0] for x in entries))
 for page,n in entries:
  if any(n in s['aliases'] for s in secs):continue
  end=next((v-1 for v in boundaries if v>page),min(page+5,len(p)));body='\n'.join(p[page-1:end]).replace('\r','');body=re.sub(r'([다요]\.)\s*(제\s*\d+조)',r'\1\n\2',body)
  matches=list(re.finditer(r'(?m)^\s*제\s*\d+조(?:의\d+)?\s*\(([^\n]+)',body));arts=[]
  for i,a in enumerate(matches):arts.append(dict(title=a[1].rstrip(') '),text=body[a.end():matches[i+1].start() if i+1<len(matches) else len(body)]))
  secs.append(dict(name=n,aliases=[n],start=page,end=end,articles=arts))
 print(k,'TOC',len(entries),'SECTIONS',len(secs))
(R/'sections.json').write_text(json.dumps(S,ensure_ascii=False),encoding='utf8')

