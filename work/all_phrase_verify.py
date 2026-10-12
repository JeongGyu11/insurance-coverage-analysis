import json
from pathlib import Path
from abl_phrase_scan import read
results=json.loads(Path('work/all_phrase/results.json').read_text(encoding='utf8'))
for x in results:
 if not x['changes']:continue
 before=json.loads(Path('work/all_phrase/'+x['name']+'_before.json').read_text(encoding='utf8'));after=read('outputs/01a10ed0-eb0e-7720-80fe-23aace7c950b/'+x['name']+'_2507_담보분석.xlsx')
 expected={v['cell']:v['new'] for v in x['changes']}
 for i,(a,b) in enumerate(zip(before,after)):
  assert a.keys()==b.keys()
  for cell,value in a.items():
   if i==0 and cell in expected:assert b[cell]==expected[cell]
   elif i==0 and cell.startswith('I') and 'G'+cell[1:] in expected:assert b[cell].endswith('+09:00')
   else:assert value==b[cell],(x['name'],i,cell)
 print('PASS',x['name'],len(expected),'all unrelated cells preserved')

