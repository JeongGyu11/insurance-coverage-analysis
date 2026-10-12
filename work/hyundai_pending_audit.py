import json,re
from pathlib import Path
R=Path('work/hyundai');P=json.loads((R/'doc5.json').read_text(encoding='utf8'));co=lambda s:re.sub(r'[\s\ufffe]','',s)
for term in ['간병인사용상해입원일당Ⅶ(1-180일)','보험료납입지원(유사암진단)','대상포진진단(10일면책)']:
 print('TERM',term)
 for i,t in enumerate(P):
  if i<120:continue
  idx=co(t).find(term)
  if idx<0:continue
  # Print just the numbered title-containing passage.
  tx=t.replace('\r','').replace('\ufffe',' ')
  for z in re.finditer(r'\d+-\d+[^\n]*(?:\n[^\n]*){0,3}',tx):
   if term in co(z[0]):print(i+1,z[0][:850])
S=json.loads((R/'sections.json').read_text(encoding='utf8'))
print('S near',[(s['name'],s['start']) for s in S['5'] if '간병인사용' in s['name']][:10])

