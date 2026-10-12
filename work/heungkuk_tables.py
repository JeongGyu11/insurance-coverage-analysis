from pathlib import Path
import json,re,pdfplumber,copy
R=Path('work/heungkuk');M=json.loads((R/'manifest.json').read_text(encoding='utf8'));out=[];cache={}
def co(s):return re.sub(r'\s+','',s or '')
def tidy(s):return re.sub(r'\s+',' ',s or '').strip()
for di in [24,27,30,33,36,39,42,45]:
 key=f'doc{di}';f=M[di]
 if f['sha256'] in cache:
  items=copy.deepcopy(cache[f['sha256']])
  for x in items:x['doc']=di
  out.extend(items);continue
 pages=json.loads((R/(key+'.json')).read_text(encoding='utf8'));items=[]
 with pdfplumber.open(f['path']) as pdf:
  for i,t in enumerate(pages):
   if '구분지급사유지급금액' not in co(t):continue
   p=pdf.pages[i].dedupe_chars()
   for ti,tab in enumerate(p.extract_tables()):
    hi=next((j for j,row in enumerate(tab) if any('지급사유'==co(v) for v in row) and any('지급금액'==co(v) for v in row)),None)
    if hi is None:continue
    h=tab[hi];ci=next(j for j,v in enumerate(h) if co(v)=='지급사유');ai=next(j for j,v in enumerate(h) if co(v)=='지급금액')
    for row in tab[hi+1:]:
     if len(row)<=ai:continue
     n=' '.join(tidy(v) for v in row[:ci] if v);c=tidy(row[ci]);a=tidy(row[ai])
     if any(v in co(n) for v in ['구분','지급사유','지급금액']):continue
     items.append(dict(doc=di,page=i+1,name=n,cause=c,amount=a))
   p.close()
 cache[f['sha256']]=items;out.extend(items);print(di,len(items),flush=True)
(R/'table_rows.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')

