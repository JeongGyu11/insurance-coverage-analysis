import json,re
from pathlib import Path
p=Path('work/mirae');out={}
for key in ['doc2','doc5','doc8']:
 a=json.loads((p/(key+'.json')).read_text(encoding='utf8'));toc=' '.join(a[1:6] if key=='doc2' else a[1:2]);toc=re.sub(r'\s+',' ',toc)
 matches=list(re.finditer(r'(.+?)\.{2,}\s*(\d+)',toc));sections=[]
 for m in matches:
  name=m[1].strip();start=int(m[2]);name=name.replace('[ 목 차 ]','').strip()
  if 'Boo' in name or 'uide' in name or '권리안내' in name or '활용동의' in name:continue
  sections.append({'name':name,'start':start})
 if key=='doc2':
  sections=[x for x in sections if x['start']!=773]+[{'name':'질병수술(백내장 및 대장용종 제외)특약(체증형)(상급종합병원)(3.10.5 간편고지)','start':767},{'name':'질병수술(백내장 및 대장용종 제외)특약(체증형)(종합병원)(3.10.5 간편고지)','start':773}]
  sections.sort(key=lambda x:x['start'])
 for i,s in enumerate(sections):s['end']=sections[i+1]['start']-1 if i+1<len(sections) else len(a)
 out[key]=sections
(p/'sections.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
for k,v in out.items():print(k,len(v),[(s['start'],s['name']) for s in v])
