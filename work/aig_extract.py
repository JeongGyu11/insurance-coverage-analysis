from pathlib import Path
import json,hashlib,pdfplumber
root=Path(r'C:\Users\FAS\Desktop\데이터분석\AIG손해보험_2507');out=Path('work/aig');out.mkdir(exist_ok=True)
manifest=[]
for i,f in enumerate(sorted(root.rglob('*.pdf'))):
 pages=[]
 with pdfplumber.open(f) as pdf:
  for p in pdf.pages:
   pages.append(p.dedupe_chars().extract_text() or '');p.close()
 key=f'doc{i}';(out/(key+'.json')).write_text(json.dumps(pages,ensure_ascii=False),encoding='utf8')
 (out/(key+'.txt')).write_text('\n'.join(f'=== PDF PAGE {n+1} ===\n{t}' for n,t in enumerate(pages)),encoding='utf8')
 manifest.append({'key':key,'path':str(f),'product_folder':f.parent.name,'kind':f.stem,'pages':len(pages),'hash':hashlib.sha256(f.read_bytes()).hexdigest()})
 (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8');print(key,f.stem,len(pages),flush=True)
