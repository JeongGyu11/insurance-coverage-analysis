import json,re
from pathlib import Path
R=Path('work/hyundai');P=json.loads((R/'doc35.json').read_text(encoding='utf8'))
co=lambda s:re.sub(r'\s+','',s)
for i,t in enumerate(P):
 if '자동차상해특별약관' in co(t) and '1.가입대상' in co(t):print('CAR',i+1,t[:650])
for di in [126,133]:
 P=json.loads((R/f'doc{di}.json').read_text(encoding='utf8'))
 print('MED source',di,[(i+1,co(t)[:80]) for i,t in enumerate(P) if '350만원' in co(t) or '250만원' in co(t) or '1일평균금액10만원' in co(t)])

