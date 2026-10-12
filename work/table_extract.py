from pathlib import Path
import json,pdfplumber,time
counts=json.loads(Path('work/counts.json').read_text(encoding='utf8'))
plans=json.loads(Path('work/table_plan.json').read_text(encoding='utf8'))
out=Path('work/cells');out.mkdir(exist_ok=True)
for d,c in enumerate(counts):
 nums=sorted({n for p in plans if p['doc']==d for n in range(p['start'],p['end']+1)})
 with pdfplumber.open(c['file']) as pdf:
  for j,n in enumerate(nums):
   target=out/f'{d}_{n}.json'
   if target.exists():continue
   p=pdf.pages[n-1].dedupe_chars()
   found=p.find_tables();tables=[]
   for tab in found:
    rows=tab.extract()
    if not any(any(v and v.strip() for v in r) for r in rows):continue
    tables.append({'bbox':list(tab.bbox),'rows':rows,'above':p.crop((0,max(0,tab.bbox[1]-65),p.width,tab.bbox[1])).extract_text() or ''})
   target.write_text(json.dumps({'doc':d,'page':n,'tables':tables,'text':p.extract_text() or ''},ensure_ascii=False),encoding='utf8')
   p.close();pdf.pages[n-1].close()
   if j%20==0:print(d,j+1,'/',len(nums),flush=True)
 print('DONE',d,flush=True)
