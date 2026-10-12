from pathlib import Path
from pypdf import PdfReader
import hashlib,json
root=Path(r'C:\Users\FAS\Desktop\데이터분석\ABL생명_2507')
out=Path('work/extracted');out.mkdir(parents=True,exist_ok=True)
manifest=[];seen={}
for f in sorted(root.rglob('*.pdf')):
 h=hashlib.sha256(f.read_bytes()).hexdigest()
 if h in seen:
  manifest.append({'path':str(f),'hash':h,'duplicate_of':seen[h]});continue
 key=f'doc{len(seen)+1}';seen[h]=key
 r=PdfReader(f);pages=[p.extract_text() or '' for p in r.pages]
 (out/(key+'.json')).write_text(json.dumps(pages,ensure_ascii=False),encoding='utf-8')
 (out/(key+'.txt')).write_text('\n'.join(f'\n=== PDF PAGE {i+1} ===\n{t}' for i,t in enumerate(pages)),encoding='utf-8')
 manifest.append({'path':str(f),'hash':h,'key':key,'pages':len(pages),'empty_pages':[i+1 for i,t in enumerate(pages) if len(t.strip())<20]})
 print(key,f.parent.name,f.name,len(pages),flush=True)
Path('work/manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
