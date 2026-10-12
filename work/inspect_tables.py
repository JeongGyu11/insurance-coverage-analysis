import json,re
from pathlib import Path
for d in [0,1,2,3]:
 f=Path(f'work/fast/p{d}.json')
 if not f.exists():continue
 pages=json.loads(f.read_text(encoding='utf8'));out=[]
 for i,t in enumerate(pages):
  c=re.sub(r'\s','',t).replace('\x00','')
  if ('지급기준표' in c and ('지급금액' in c or '지급액' in c or '지급사유' in c)) and re.search(r'[\[（(【]별표\d',c):
   out.append({'page':i+1,'text':t})
 Path(f'work/tables{d}.json').write_text(json.dumps(out,ensure_ascii=False),encoding='utf8')
 Path(f'work/tables{d}.txt').write_text('\n'.join(f"=== PAGE {a['page']} ===\n{a['text']}" for a in out),encoding='utf8')
 print(d,len(out),[a['page'] for a in out[:15]])
