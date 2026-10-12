import json,re,bisect,copy
from pathlib import Path
R=Path('work/hyundai');M=json.loads((R/'manifest.json').read_text(encoding='utf8'));out={};cache={}
def co(s):return re.sub(r'[\s\ufffe\x00\uf000-\uf8ff]','',s or '')
def clean(s):return re.sub(r'[\s\ufffe\x00\uf000-\uf8ff]+',' ',s or '').strip()
for di,m in enumerate(M):
 if m['kind']!='약관':continue
 if m['sha256'] in cache:out[str(di)]=copy.deepcopy(cache[m['sha256']]);continue
 P=json.loads((R/f'doc{di}.json').read_text(encoding='utf8'))
 P=[re.sub(r'[\ufffe\x00\uf000-\uf8ff]',' ',t.replace('\r','')) for t in P]
 P=[re.sub(r'([다요]\.)\s*(제\s*\d+\s*조)',r'\1\n\2',t) for t in P]
 starts=[];pos=0
 for t in P:starts.append(pos);pos+=len(t)+1
 flow='\n'.join(P);secs=[];motor='자동차보험' in m['product'];travel='해외' in m['product']
 if motor:
  heads=list(re.finditer(r'(?m)^[ \t]*(?:\d{1,3}[ \t]+)?([^\n]{2,100})[ \t]+특별약관[ \t]*$',flow))
  for z in heads:
   name=clean(z[1]);after=flow[z.end():z.end()+650]
   ma=re.search(r'(?:^|\n)\s*1\.\s*(?:가입대상|보상하는|보상내용|적용대상|피보험자|특약의|보험금)',after)
   if not ma or ma.start()>400 or '··' in name:continue
   secs.append(dict(name=co(name),aliases=[co(name)],start_char=z.start(),textstart=z.end(),start=bisect.bisect_right(starts,z.start()),number=''))
 else:
  for a in re.finditer(r'제\s*1\s*조\s*\(',flow):
   origin=max(0,a.start()-2400);prefix=flow[origin:a.start()]
   # Actual health rider title numbers have a hyphen; they are not article subparagraphs.
   hh=list(re.finditer(r'(?<![\d가-힣])(\d+(?:-\d+)+)\.?[ \t]+',prefix))
   if not travel and hh:
    z=hh[-1];chunk=prefix[z.end():]
    ends=list(re.finditer(r'특별약\s*관[ \t]*(?=\n|$|/)',chunk))
    if not ends:continue
    end=ends[-1].end();between=chunk[end:]
    if re.search(r'제\s*\d+\s*조',between):continue
    title=chunk[:end];st=origin+z.start()
    # Remove page/sidebar artifacts from titles, preserving actual aliases.
    lines=[l.strip() for l in title.splitlines() if l.strip()]
    lines=[l for l in lines if not re.match(r'^\d+\s+무배당',l) and l not in ['특별','약관','상해','질병','비용','손해','및','독립','특약','기타','특별약관']]
    title=clean(' '.join(lines));num=z[1]
   else:
    hh=list(re.finditer(r'(?m)^[ \t]*([^\n]{2,140}특별약\s*관)[ \t]*$',prefix))
    if not hh:continue
    z=hh[-1];between=prefix[z.end():]
    if re.search(r'제\s*\d+\s*조',between):continue
    title=clean(z[1]);st=origin+z.start();num=''
   if '··' in title or len(title)>350 or not title:continue
   title=title.removesuffix('특별약관').strip()
   aliases=[co(v).removesuffix('보장') for v in re.split(r'특별약관\s*/\s*|\s*/\s*(?=[가-힣])',title)]
   secs.append(dict(name=co(title),aliases=aliases,start_char=st,textstart=a.start(),start=bisect.bisect_right(starts,st),number=num))
 secs.sort(key=lambda x:x['start_char']);unique=[]
 for s in secs:
  if unique and abs(s['start_char']-unique[-1]['start_char'])<4:continue
  unique.append(s)
 secs=unique
 for i,s in enumerate(secs):
  end=secs[i+1]['start_char'] if i+1<len(secs) else len(flow)
  s['end']=bisect.bisect_right(starts,max(s['textstart'],end-1));body=flow[s['textstart']:end]
  aa=list(re.finditer(r'제\s*(\d+)\s*조(?:의\s*\d+)?\s*\(([^\n]+)',body))
  if not aa:aa=list(re.finditer(r'(?m)^\s*(\d+)\.\s*([^\n]{2,80})',body))
  s['articles']=[dict(number=a[1],title=a[2].rstrip(') '),text=body[a.end():aa[j+1].start() if j+1<len(aa) else len(body)].strip()) for j,a in enumerate(aa)]
  s['body']=body
  for k in ['start_char','textstart']:s.pop(k)
 out[str(di)]=secs;cache[m['sha256']]=secs;print(di,len(secs),[s['name'][:55] for s in secs[:2]],flush=True)
(R/'sections.json').write_text(json.dumps(out,ensure_ascii=False),encoding='utf8')



