import json,re
from pathlib import Path
import pdfplumber
root=Path('work/fubon');m=json.loads((root/'manifest.json').read_text(encoding='utf8'))
def clean(s):
 return re.sub(r'\s+',' ',re.sub(r'[\ue000-\uf8ff]','',s or '')).strip()
out=[]
for di in [1,3,5]:
 texts=json.loads((root/f'doc{di}.json').read_text(encoding='utf8'));pdf=pdfplumber.open(m[di]['path'])
 for i,t in enumerate(texts):
  if not re.search(r'별표\s*1[-－]1\s*보험금지급기준표',t):continue
  if any(v['doc']==di and v['page']==i+1 for v in out):continue
  entries=[]
  for j in range(i,min(i+3,len(texts))):
   if j>i and (re.search(r'별표\s*1-2|별표\s*2',texts[j]) or di!=1):break
   p=pdf.pages[j];lines=p.lines
   heads=[w for w in p.extract_words() if w['text']=='구분'];edges=None
   for h in heads:
    ls=[l for l in lines if abs(l['top']-h['top']+3.5)<3 and l['x1']-l['x0']>20]
    ls=sorted({(round(l['x0'],1),round(l['x1'],1)) for l in ls})
    if len(ls)==3:edges=[ls[0][0]-1,(ls[0][1]+ls[1][0])/2,(ls[1][1]+ls[2][0])/2,ls[2][1]+1];break
   if not edges:edges=[48,113.4,295.4,390]
   tables=p.extract_tables({'vertical_strategy':'explicit','explicit_vertical_lines':edges,'intersection_tolerance':7,'snap_tolerance':2,'join_tolerance':7})
   for tab in tables:
    active=False;previous=''
    for row in tab:
     if len(row)!=3:continue
     r=[clean(v) for v in row]
     if r[0]=='구분' and '지급' in r[1]:active=True;previous='';continue
     if active and not r[0] and r[1] and r[2] and '(기준' not in r[1]:r[0]=previous
     if r[0] and r[0]!='구분' and (active or j>i) and r[1] and r[2]:
      entries.append(dict(page=j+1,name=r[0],target=r[1],amount=r[2]));previous=r[0]
  ct=clean(t);start=ct.find('주)');notes=ct[start:] if start>=0 else ''
  if i+1<len(texts) and '별표' not in texts[i+1][:1000]:notes+=' '+clean(texts[i+1])
  out.append(dict(doc=di,page=i+1,title=clean(t.split('\r')[0]),basis=re.findall(r'\(기준\s*:[^)]+\)',ct),rows=entries,notes=notes))
  print(di,i+1,len(entries),flush=True)
 pdf.close()
(root/'tables.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
