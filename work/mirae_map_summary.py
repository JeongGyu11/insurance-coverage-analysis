import json,re,difflib
from pathlib import Path
p=Path('work/mirae');s=json.loads((p/'sections.json').read_text(encoding='utf8'))['doc2'];s=[x for x in s if x['start']<977]
def norm(t):
 for a,b in [('특얛','특약'),('특얯','특약'),('특Q-F','특약'),('특Q-K','특약'),('특Q-X','특약'),('제증','체증'),('지료','치료'),('되','뇌'),('제오l','제외'),('제오','제외'),('제와','제외'),('기F-I','기타'),('기다피부암','기타피부암'),('산정특레','산정특례')]:t=t.replace(a,b)
 t=re.split(r'\(?3\.?\s*10|\[기본',t)[0]
 return re.sub(r'[^가-힣a-zA-Z0-9]','',t).lower()
a=json.loads((p/'doc1_ocr.json').read_text(encoding='utf8'));out={str(x['start']):{'name':x['name'],'pages':[],'text':''} for x in s};cur=45
for i,t in enumerate(a[7:56],8):
 lines=t.splitlines()
 for j,line in enumerate(lines):
  if re.match(r'^[口□]\s*',line):
   title=line[1:]+(' '+lines[j+1] if j+1<len(lines) and '十' not in lines[j+1] else '')
   scored=sorted([(difflib.SequenceMatcher(None,norm(title),norm(z['name'])).ratio(),z['start']) for z in s],reverse=True)
   if scored[0][0]>.45:cur=scored[0][1]
  entry=out[str(cur)];entry['text']+=line+'\n'
  if i not in entry['pages']:entry['pages'].append(i)
(p/'summary_map.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
for k,v in out.items():print(k,','.join(map(str,v['pages'])),v['name'])
