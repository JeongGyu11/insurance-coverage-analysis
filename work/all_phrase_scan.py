import json,re
from pathlib import Path
from abl_phrase_scan import read
root=Path('C:/Users/FAS/Desktop/데이터분석');results=[]
names=['NH농협생명','NH농협손해보험','교보생명','롯데손해보험','미래에셋생명','신한라이프','푸본현대생명']
for name in names:
 p=root/(name+'_2507_담보분석.xlsx');d=read(p);assert d[0]['G1']=='coverage_conditions'
 rows=[(c,s) for c,s in d[0].items() if re.fullmatch(r'G[2-9]\d*|G1\d+',c)]
 exact=[];similar=[]
 for c,s in rows:
  new=re.sub(r'해당\s*특약을\s*가입한\s*계약에\s*적용합니다\.[ \t]*','',s).strip()
  if new!=s:exact.append(dict(cell=c,old=s,new=new))
  for sentence in re.split(r'(?<=[.!?])\s+',s):
   if '특약' in sentence and ('가입' in sentence or '부가' in sentence) and ('적용' in sentence or '계약에' in sentence):similar.append(dict(cell=c,text=sentence))
 result=dict(name=name,path=str(p),rows=len(rows),changes=exact,similar=similar)
 results.append(result);print(name,len(rows),'EXACT',len(exact),'SIMILAR',len(similar))
 for v in similar[:4]:print(v)
Path('work/all_phrase').mkdir(exist_ok=True)
Path('work/all_phrase/results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf8')

