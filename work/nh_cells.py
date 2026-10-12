from pathlib import Path
import json,pdfplumber
out=Path('work/nh');m=json.loads((out/'manifest.json').read_text(encoding='utf8'));result=[]
for key,n in [('doc2',n) for n in [107,108,109,110,111,112,132,144,157,170,183]]+[('doc3',n) for n in [102,103,104,105]]:
 entry=next(a for a in m if a['key']==key)
 with pdfplumber.open(entry['path']) as pdf:
  p=pdf.pages[n-1].dedupe_chars();tabs=[]
  for t in p.find_tables():
   rows=t.extract();header=t.rows[0].cells
   for i,rr in enumerate(t.rows[1:],1):
    known=next((c for c in rr.cells if c),None)
    if not known:continue
    for col in [0,2]:
     if len(rows[i])>col and len(header)>col and rows[i][col] is None and header[col]:rows[i][col]=p.crop((header[col][0],known[1],header[col][2],known[3])).extract_text() or ''
   tabs.append({'bbox':list(t.bbox),'rows':rows})
  result.append({'key':key,'page':n,'tables':tabs,'text':p.extract_text()})
(out/'cells.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(result,ensure_ascii=False,indent=2))

