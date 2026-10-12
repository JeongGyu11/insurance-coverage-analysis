from pathlib import Path
import pdfplumber,hashlib,json
root=Path(r'C:\Users\FAS\Desktop\데이터분석\ABL생명_2507');out=Path('work/plumber');out.mkdir(exist_ok=True)
manifest=[];seen={}
for f in sorted(root.rglob('*.pdf')):
 h=hashlib.sha256(f.read_bytes()).hexdigest()
 if h in seen:
  manifest.append({'path':str(f),'hash':h,'duplicate_of':seen[h]});continue
 key=f'doc{len(seen)+1}';seen[h]=key
 pages=[]
 with pdfplumber.open(f) as pdf:
  for i,p in enumerate(pdf.pages):
   pages.append(p.dedupe_chars().extract_text() or '');p.close()
   if i%200==0:print(key,i,flush=True)
 (out/(key+'.json')).write_text(json.dumps(pages,ensure_ascii=False),encoding='utf-8')
 (out/(key+'.txt')).write_text('\n'.join(f'\n=== PDF PAGE {i+1} ===\n{t}' for i,t in enumerate(pages)),encoding='utf-8')
 manifest.append({'path':str(f),'hash':h,'key':key,'pages':len(pages),'empty_pages':[i+1 for i,t in enumerate(pages) if len(t.strip())<20]})
 Path('work/plumber_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
 print(key,len(pages),'done',flush=True)

