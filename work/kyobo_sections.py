from pathlib import Path
import json,re
p=Path('work/kyobo');m=json.loads((p/'manifest.json').read_text(encoding='utf8'));allsections={}
for f in m:
 if f['kind']!='약관':continue
 a=json.loads((p/(f['key']+'.json')).read_text(encoding='utf8'));starts=[]
 for i,t in enumerate(a):
  match=re.search(r'(?m)^제\s*1\s*조\s*\(목적\)\s*$',t)
  if not match:continue
  prefix=t[:match.start()].split('제1관')[0];name=re.sub(r'\s+',' ',prefix).strip();name=re.sub(r'￡[^￡]+￡','',name).strip();name=name.split('※')[0].strip();name=re.sub(r'약\s*관\s*$','',name).strip()
  starts.append({'name':name,'start':i+1})
 for j,s in enumerate(starts):
  s['end']=starts[j+1]['start']-1 if j+1<len(starts) else len(a)
  body='\n'.join(a[s['start']-1:s['end']]);articles=[];hits=list(re.finditer(r'(?m)^제\s*\d+\s*조(?:의\d+)?\s*\(([^\n]+)\)\s*$',body))
  for k,h in enumerate(hits):articles.append({'title':h.group(1),'text':body[h.start():hits[k+1].start() if k+1<len(hits) else len(body)]})
  s['articles']=articles
 allsections[f['key']]=starts
(p/'sections.json').write_text(json.dumps(allsections,ensure_ascii=False),encoding='utf8')
for key,ss in allsections.items():
 print(key,len(ss))
 for s in ss:print(s['start'],s['end'],s['name'])
