import json,re
from pathlib import Path
import pdfplumber
R=Path('work/heungkuk_life');M=json.loads((R/'manifest.json').read_text(encoding='utf8'))
def c(s):return re.sub(r'\s+',' ',s or '').strip()
out=[]
for di in [1,3,5]:
 P=json.loads((R/f'doc{di}.json').read_text(encoding='utf8'))
 with pdfplumber.open(M[di]['path']) as pdf:
  for i,t in enumerate(P):
   if not re.search(r'^\s*\d*\s*\(별표\s*1\)\s*보험금\s*지급기준표',t):continue
   for j in range(i,min(i+5,len(P))):
    if j>i and ('별표' in P[j][:200] or not re.search(r'급\s*여\s*명',P[j])):break
    page=pdf.pages[j];tabs=[]
    for tab in page.find_tables():
     rows=tab.extract()
     if not rows or '급여명' not in re.sub(r'\s+','',str(rows[0])):continue
     before=page.crop((0,0,page.width,max(1,tab.bbox[1]))).extract_text() or ''
     tabs.append(dict(rows=rows,before=before))
    notes=t
    if j==i:
     for k in range(i+1,min(i+3,len(P))):
      if re.search(r'별표\s*[2-9]|제\s*1\s*관|급\s*여\s*명',P[k][:500]):break
      notes+=' '+P[k]
    out.append(dict(doc=di,page=j+1,text=P[j],tables=tabs,notes=notes))
 print(di,len([x for x in out if x['doc']==di]),flush=True)
(R/'tables.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
# Section table-of-contents pages: printed page is always PDF page +2.
S={}
for di in [1,3,5]:
 P=json.loads((R/f'doc{di}.json').read_text(encoding='utf8'))
 sec=[]
 for i,t in enumerate(P):
  if i<10:continue
  flat=c(t)
  z=re.search(r'^\d+\s+(무배당.*?)\s*제\s*1\s*관\s*목적',flat)
  if z and '···' in flat[:1000]:
   title=re.sub(r'\[가입자에 한함\]','',z[1]).strip()
   sec.append(dict(page=i+1,title=title))
 S[str(di)]=sec
 print('SECTIONS',di,[(s['page'],s['title'][:35]) for s in sec])
(R/'sections.json').write_text(json.dumps(S,ensure_ascii=False,indent=2),encoding='utf8')

