import json
from pathlib import Path
from abl_phrase_scan import read
p=Path('work/all_phrase/results.json');r=json.loads(p.read_text(encoding='utf8'))
phrases={'NH농협생명':'특약 선택 가입 및 해당 보험료 납입 시 적용.','교보생명':'해당 특약은 실제 가입한 계약에 적용합니다.'}
for x in r:
 if x['name'] not in phrases:continue
 d=read(x['path']);Path('work/all_phrase/'+x['name']+'_before.json').write_text(json.dumps(d,ensure_ascii=False),encoding='utf8')
 for cell,s in d[0].items():
  if cell.startswith('G') and phrases[x['name']] in s:x['changes'].append(dict(cell=cell,old=s,new=s.replace(phrases[x['name']],'').strip()))
 print(x['name'],len(x['changes']))
p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')

