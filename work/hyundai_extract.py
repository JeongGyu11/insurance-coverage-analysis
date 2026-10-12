from pathlib import Path
import json,hashlib
import pypdfium2 as pdfium
p=Path('work/hyundai');p.mkdir(exist_ok=True)
root=Path('C:/Users/FAS/Desktop/데이터분석/현대해상_2507');m=[]
for i,f in enumerate(sorted(root.rglob('*.pdf'))):
 r=pdfium.PdfDocument(str(f));pages=[x.get_textpage().get_text_range() for x in r];key=f'doc{i}'
 (p/f'{key}.json').write_text(json.dumps(pages,ensure_ascii=False),encoding='utf8')
 (p/f'{key}.txt').write_text('\n'.join(f'\n### PDF {n+1}\n{t}' for n,t in enumerate(pages)),encoding='utf8')
 m.append(dict(key=key,path=str(f),product=f.parent.name,kind=f.stem,pages=len(pages),sha256=hashlib.sha256(f.read_bytes()).hexdigest(),chars=sum(map(len,pages))))
(p/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf8')
for x in m:print(x['key'],x['product'],x['kind'],x['pages'],x['chars'],x['sha256'][:12])



