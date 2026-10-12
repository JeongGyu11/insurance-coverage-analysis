from pathlib import Path
import pdfplumber,json
root=Path(r'C:\Users\FAS\Desktop\데이터분석\AIG손해보험_2507');out=Path('work/aig');out.mkdir(exist_ok=True)
result=[]
for d,f in enumerate(sorted(root.rglob('상품요약서.pdf'))):
 with pdfplumber.open(f) as pdf:
  active=False
  for i,page in enumerate(pdf.pages):
   p=page.dedupe_chars();text=p.extract_text() or ''
   if 'Ⅱ. 보험금 지급사유' in text:active=True
   if active and ('Ⅲ.' in text or 'Ⅲ .' in text):active=False
   if active:
    tables=[{'bbox':list(t.bbox),'rows':t.extract()} for t in p.find_tables()]
    result.append({'doc':d,'path':str(f),'product':f.parent.name.split('_무배당_',1)[1].replace('_',' '),'page':i+1,'text':text,'tables':tables})
   p.close();page.close()
 print('summary',d,flush=True)
(out/'summary_tables.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
