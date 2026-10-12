from pathlib import Path
import json,pdfplumber,re
root=Path(r'C:\Users\FAS\Desktop\데이터분석\AIG손해보험_2507');out=Path('work/aig');result=[]
for d,f in enumerate(sorted(root.rglob('상품요약서.pdf'))):
 with pdfplumber.open(f) as pdf:
  active=False
  for i,page in enumerate(pdf.pages):
   p=page.dedupe_chars();text=p.extract_text() or ''
   if 'Ⅱ. 보험금 지급사유' in text:active=True
   if active and ('Ⅲ.' in text or 'Ⅲ .' in text):active=False
   if not active:p.close();page.close();continue
   # Thin horizontal border rectangles bound the left benefit-name cells.
   boundaries=sorted({round(r['top'],1) for r in p.rects if 70<r['x0']<100 and r['x1']>190 and r['height']<1 and r['width']>100})
   for a,b in zip(boundaries,boundaries[1:]):
    if b-a<10:continue
    name=p.crop((75,a+0.5,195.5,b)).extract_text() or ''
    desc=p.crop((196.5,a+0.5,541,b)).extract_text() or ''
    if '[갱신형]' in name:
     result.append({'doc':d,'summary_path':str(f),'product':'무배당 '+f.parent.name.split('_무배당_',1)[1].replace('_',' '),'page':i+1,'name':name.replace('\n',''),'description':desc,'bbox':[75,a,541,b]})
    elif result and result[-1]['doc']==d and i+1==result[-1]['page']+1 and a<140 and desc and not name.strip():
     result[-1]['description']+='\n'+desc;result[-1]['end_page']=i+1
   p.close();page.close()
 print(d,'rows',sum(x['doc']==d for x in result),flush=True)
(out/'benefits.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
