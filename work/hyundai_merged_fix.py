import json,re
from pathlib import Path
R=Path('work/hyundai');T=json.loads((R/'tables.json').read_text(encoding='utf8'))
co=lambda s:re.sub(r'\s+','',s or '')
for t in T:
 if t['doc'] in [4,16] and t['page'] in [18,30]:
  for row in t['rows'][t['header']+1:]:
   row[t['ai']]='각 세부보장 가입금액(각각 최초 1회한). 최초계약일부터 1년 미만에는 해당 금액의 50%.'
 if t['doc']==61 and t['page']==41:
  for row in t['rows'][t['header']+1:]:row[t['ai']]='특약가입금액(각각 연간 1회한)'
 if t['doc'] in [88,100] and t['page']==13 and any('월지급형' in co(''.join(v or '' for v in row)) for row in t['rows']):
  for row in t['rows'][t['header']+1:]:row[t['ai']]='보험금 지급기간 동안 보험증권에 정한 월지급액을 매월 확정지급(최초 1회한)'
(R/'tables.json').write_text(json.dumps(T,ensure_ascii=False,indent=2),encoding='utf8');print('MERGED AMOUNTS REPAIRED')

