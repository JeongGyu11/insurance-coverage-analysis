from pathlib import Path
import json,re,subprocess
from concurrent.futures import ThreadPoolExecutor
p=Path('work/shinhan');m=json.loads((p/'manifest.json').read_text(encoding='utf8'))
a=json.loads((p/'doc1.json').read_text(encoding='utf8'));b=json.loads((p/'doc5.json').read_text(encoding='utf8'))
def norm(t):
 t=re.sub(r'22121522000000\d{4}|2246\d{4}','',t)
 t=t.replace('신한SOL메이트달러연금보험','SOL메이트달러연금보험')
 return re.sub(r'\s+','',t)
diffs=[i+1 for i,(x,y) in enumerate(zip(a,b)) if norm(x)!=norm(y)]
print('Product-name/document-code-normalized different pages:',diffs)
for n in diffs:
 if n!=1: print(n, norm(a[n-1])[:80],norm(b[n-1])[:80])
jobs=[('doc1',n) for n in [67,68,69]]+[('doc3',n) for n in [33,34,35,36,76,77]]+[('doc0',4),('doc2',3)]
def render(job):
 key,n=job;f=next(x['path'] for x in m if x['key']==key)
 prefix=str(p/f'{key}_{n}')
 subprocess.run(['pdftoppm','-f',str(n),'-l',str(n),'-scale-to','1800','-png','-singlefile',f,prefix],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 return prefix+'.png'
with ThreadPoolExecutor(max_workers=3) as ex:
 for f in ex.map(render,jobs):print(f)
