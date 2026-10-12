import json,re
from pathlib import Path
p=Path('work/lotte');out={}
for key in ['doc2','doc5']:
 a=json.loads((p/(key+'.json')).read_text(encoding='utf8'));starts=[]
 side=set('유의사항요약서해설주분쟁례특별관보통목차입자가험내용오인하기쉬운')
 a=['\n'.join(re.sub(r'^(제\s*\d+조(?:의\d+)?\s*\([^\n]+\))\s+['+''.join(side)+r']$',r'\1',line) for line in t.split('\n') if line.strip() not in side and line.strip() not in ['유 가','의 입','사 자','요 주','약 요','서 내','해 보','설 험','주 오','요 인','사 쉬','례 운'] and not line.startswith('let:') and not re.fullmatch(r'\d{1,3}',line.strip())) for t in a]
 (p/(key+'_clean.json')).write_text(json.dumps(a,ensure_ascii=False),encoding='utf8')
 for i,t in enumerate(a):
  if i<20:continue
  if re.search(r'(?m)^제1조\s*\(목적\)',t) and not starts:starts.append({'name':'보통약관','start':i+1});continue
  head=t[:900];hit=re.search(r'(?m)^제1조\s*\(',head)
  if hit:
   prefix=head[:hit.start()].strip();prefix=re.sub(r'^특\s*별\s*약\s*관\s*','',prefix).strip();prefix=re.sub(r'\s+',' ',prefix)
   if '특별약관' in prefix and len(prefix)<350:
    name=prefix.split('특별약관')[0]+'특별약관'+prefix.split('특별약관')[1].split('□')[0].split('실손의료비')[0].split('제1관')[0]
    starts.append({'name':name.strip(),'start':i+1})
 for i,s in enumerate(starts):
  s['end']=starts[i+1]['start']-1 if i+1<len(starts) else len(a);body='\n'.join(a[s['start']-1:s['end']]);hits=list(re.finditer(r'(?m)^제\s*(\d+)조(?:의\d+)?\s*\(([^)\n]+)\)\s*$',body));s['articles']=[]
  for j,h in enumerate(hits):
   text=body[h.start():hits[j+1].start() if j+1<len(hits) else len(body)];s['articles'].append({'number':int(h.group(1)),'title':h.group(2),'text':text})
 out[key]=starts
(p/'sections.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
for k,ss in out.items():
 print(k,len(ss))
 for s in ss:print(s['start'],s['end'],s['name'],[(a['number'],a['title']) for a in s['articles'][:3]])
