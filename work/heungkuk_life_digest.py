import json,re
from pathlib import Path
R=Path('work/heungkuk_life');T=json.loads((R/'tables_raw.json').read_text(encoding='utf8'))
for di in [1,3,5]:
 P=json.loads((R/f'doc{di}.json').read_text(encoding='utf8'))
 out=[]
 for x in T:
  if x['doc']!=di:continue
  out.append(f"\nPAGE {x['page']}\n"+x['text'])
  if x['page']<len(P) and not re.search(r'별표\s*[2345]|제\s*1\s*관',P[x['page']][:200]):out.append(P[x['page']])
 (R/f'digest{di}.txt').write_text('\n'.join(out),encoding='utf8')
 print(di,'EMPTY',[(x['page']) for x in T if x['doc']==di and not x['tables']])

