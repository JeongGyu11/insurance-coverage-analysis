import json,re,bisect
from pathlib import Path
R=Path('work/heungkuk');M=json.loads((R/'manifest.json').read_text(encoding='utf8'));out={}
def co(s):return re.sub(r'\s+','',s or '')
for di in [25,28,31,34,37,40,43,46]:
 pages=json.loads((R/f'doc{di}.json').read_text(encoding='utf8'));pages=[re.sub(r'([다요]\.)\s*(제\s*\d+조)',r'\1\n\2',t) for t in pages];pages=[re.sub(r'(?m)^\s*-\s*\d+\s*-\s*$','',t.replace('\r','')) for t in pages]
 starts=[];pos=0
 for t in pages:starts.append(pos);pos+=len(t)+1
 body='\n'.join(pages);sections=[]
 for art in re.finditer(r'(?m)^\s*제\s*1조\s*\(',body):
  prefix=body[max(0,art.start()-1800):art.start()]
  titles=list(re.finditer(r'(?m)^\s*(\d+(?:-\d+)*\.)\s*([^\n]*(?:\n(?!\s*(?:제\s*\d+조|\d+(?:-\d+)*\.))[^\n]*){0,5}?)\s*특별약관\s*$',prefix))
  if not titles:continue
  # collect only adjacent aliases at the end of the preamble
  group=titles[-1];aliases=[co(z.group(2)) for z in titles if group.start()-z.end()<900 and not re.search(r'제\s*\d+조',prefix[z.end():group.start()])]
  name=aliases[0];st=max(0,art.start()-1800)+next(z.start() for z in titles if co(z.group(2))==name)
  if sections and st<=sections[-1]['start_char']:continue
  sections.append(dict(name=name,aliases=aliases,start_char=st,article_start=art.start(),start=bisect.bisect_right(starts,st)))
 for i,s in enumerate(sections):
  end=sections[i+1]['start_char'] if i+1<len(sections) else len(body)
  s['end']=bisect.bisect_right(starts,max(s['article_start'],end-1));text=body[s['article_start']:end];articles=[]
  matches=list(re.finditer(r'(?m)^\s*제\s*(\d+)조(?:의\d+)?\s*\(([^\n]+)',text))
  for j,a in enumerate(matches):
   title=a[2].rstrip(') ').strip();endart=matches[j+1].start() if j+1<len(matches) else len(text)
   articles.append(dict(title=title,text=text[a.end():endart].strip()))
  s['articles']=articles;s.pop('start_char');s.pop('article_start')
 out[str(di)]=sections;print(di,len(sections),[s['name'] for s in sections[:4]],flush=True)
(R/'sections.json').write_text(json.dumps(out,ensure_ascii=False),encoding='utf8')



