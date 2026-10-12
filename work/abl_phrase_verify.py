from abl_phrase_scan import read
from pathlib import Path
import json
before=json.loads(Path('work/abl_phrase/before.json').read_text(encoding='utf8'))
changes=json.loads(Path('work/abl_phrase/changes.json').read_text(encoding='utf8'))
after=read('outputs/01a10ed0-eb0e-7720-80fe-23aace7c950b/ABL생명_2507_담보분석.xlsx')
expected={x['cell']:x['new'] for x in changes}
modified=0
for i,(a,b) in enumerate(zip(before,after)):
 assert a.keys()==b.keys(),i
 for cell,value in a.items():
  if i==0 and cell in expected:assert b[cell]==expected[cell];modified+=1
  elif i==0 and cell.startswith('I') and 'G'+cell[1:] in expected:assert b[cell].endswith('+09:00')
  else:assert value==b[cell],(i,cell,value,b[cell])
assert modified==587
assert not any('해당 특약을 가입한 계약에 적용합니다.' in v for k,v in after[0].items() if k.startswith('G'))
print('PASS',modified,'conditions changed; every unrelated cell unchanged; 650 rows preserved')

