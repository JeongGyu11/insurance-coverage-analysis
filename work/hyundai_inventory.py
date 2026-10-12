import json,hashlib,re
from pathlib import Path
R=Path('work/hyundai');root=Path('C:/Users/FAS/Desktop/데이터분석/현대해상_2507')
m=[]
for i,f in enumerate(sorted(root.rglob('*.pdf'))):
 m.append(dict(key=f'doc{i}',path=str(f),product=f.parent.name,kind=f.stem,sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
(R/'inventory.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf8')
print('unique',len(set(x['sha256'] for x in m)),'total',len(m))

