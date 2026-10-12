import json,re,copy
from pathlib import Path
import pdfplumber,pypdfium2 as pdfium
R=Path('work/hyundai');M=json.loads((R/'inventory.json').read_text(encoding='utf8'));out=[];cache={}
def co(s):return re.sub(r'[\s\ufffe\x00]','',s or '')
def clean(s):return re.sub(r'[\s\ufffe\x00]+',' ',s or '').strip()
for di,m in enumerate(M):
 if m['kind']!='상품요약서':continue
 if m['sha256'] in cache:
  a=copy.deepcopy(cache[m['sha256']]);[x.update(doc=di) for x in a];out+=a;continue
 jf=R/f'doc{di}.json'
 P=json.loads(jf.read_text(encoding='utf8')) if jf.exists() else [p.get_textpage().get_text_range() for p in pdfium.PdfDocument(m['path'])]
 found=[]
 with pdfplumber.open(m['path']) as pdf:
  for i,t in enumerate(P):
   if '지급사유' not in co(t) or not any(v in co(t) for v in ['지급금액','보장금액']):continue
   page=pdf.pages[i].dedupe_chars()
   for ti,tab in enumerate(page.find_tables()):
    raw=tab.extract();hi=next((j for j,row in enumerate(raw) if any(co(v) in ['지급사유','보험금지급사유'] for v in row) and any(co(v) in ['지급금액','보장금액'] for v in row)),None)
    if hi is None:continue
    h=raw[hi];ci=next(j for j,v in enumerate(h) if co(v) in ['지급사유','보험금지급사유']);ai=next(j for j,v in enumerate(h) if co(v) in ['지급금액','보장금액'])

    # Open right borders cause pdfplumber to return None despite visible amount text.
    # Reconstruct the amount rectangle from the header and row's intersecting cells.
    for ri,row in enumerate(raw):
     if ri<=hi:continue
     if len(row)>ai and not row[ai]:
      hc=tab.rows[hi].cells[ai]
      cells=[cell for cell in tab.rows[ri].cells[:ai] if cell]
      if hc and cells:
       top=max(cell[1] for cell in cells);bottom=min(cell[3] for cell in cells)
       if bottom>top+2:
        recovered=page.crop((hc[0],top,hc[2],bottom)).extract_text() or ''
        if recovered.strip():raw[ri][ai]=recovered
    found.append(dict(doc=di,page=i+1,table=ti,bbox=tab.bbox,header=hi,ci=ci,ai=ai,rows=raw,above=page.crop((0,0,page.width,max(1,tab.bbox[1]))).extract_text() or ''))
 cache[m['sha256']]=found;out+=found;print(di,m['product'][:55],len(found),flush=True)
(R/'tables.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print('TABLES',len(out))


