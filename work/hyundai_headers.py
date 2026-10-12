import json,re,bisect
from pathlib import Path
R=Path('work/hyundai');M=json.loads((R/'manifest.json').read_text(encoding='utf8'));S=json.loads((R/'sections.json').read_text(encoding='utf8'))
def co(s):return re.sub(r'[\s\ufffe\x00\uf000-\uf8ff]','',s or '')
for di,m in enumerate(M):
 if m['kind']!='약관' or any(v in m['product'] for v in ['자동차보험','해외','실손의료','금리혼합','할인','중지']):continue
 P=json.loads((R/f'doc{di}.json').read_text(encoding='utf8'));P=[re.sub(r'[\ufffe\x00\uf000-\uf8ff]',' ',t.replace('\r','')) for t in P];P=[re.sub(r'특\s*별\s*약\s*관','특별약관',t) for t in P];starts=[];off=0
 for t in P:starts.append(off);off+=len(t)+1
 flow='\n'.join(P);heads=[]
 # Scan actual numbered headings directly rather than relying on a fixed preamble length.
 for z in re.finditer(r'(?<![\d가-힣])(\d+(?:-\d+)+)\.?[ \t]+',flow):
  tail=flow[z.end():z.end()+500];end=re.search(r'특별약\s*관',tail)
  if not end:continue
  title=tail[:end.start()]
  if re.search(r'제\s*\d+\s*조|··|다\.|니다\.|경우에는',title) or len(co(title))<5 or len(title)>220:continue
  page=bisect.bisect_right(starts,z.start())
  if page<40:continue
  aliases=[co(title).removesuffix('보장')];lastend=z.end()+end.end()
  rest=flow[lastend:lastend+1200]
  while re.match(r'\s*/',rest):
   rest=re.sub(r'^\s*/\s*','',rest);ee=re.search(r'특별약\s*관',rest)
   if not ee or ee.start()>250:break
   aliases.append(co(rest[:ee.start()]).removesuffix('보장'));rest=rest[ee.end():]
  fullalias=[]
  for a in aliases:
   fullalias.extend(co(v).removesuffix('보장') for v in re.split(r'/\s*(?=간병인|질병|상해|암|뇌|통합|급성|보험료|항암|소액|표적|심|특정|간호|납입)',a))
  aliases=list(dict.fromkeys(fullalias))
  heads.append(dict(name=co(title),aliases=aliases,start_char=z.start(),textstart=lastend,start=page,number=z[1]))
 for i,s in enumerate(heads):
  en=heads[i+1]['start_char'] if i+1<len(heads) else len(flow);s['end']=bisect.bisect_right(starts,max(en-1,s['textstart']));body=flow[s['textstart']:en]
  aa=list(re.finditer(r'제\s*(\d+)\s*조(?:의\s*\d+)?\s*\(([^\n]+)',body))
  s['articles']=[dict(number=a[1],title=a[2].rstrip(') '),text=body[a.end():aa[j+1].start() if j+1<len(aa) else len(body)].strip()) for j,a in enumerate(aa)];s['body']=body
  for k in ['start_char','textstart']:s.pop(k)
 S[str(di)]=heads;print(di,len(heads),[s['name'] for s in heads[:2]],flush=True)
(R/'sections.json').write_text(json.dumps(S,ensure_ascii=False),encoding='utf8')


