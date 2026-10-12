import json,subprocess
from pathlib import Path
p=Path('work/lotte');m=json.loads((p/'manifest.json').read_text(encoding='utf8'));exe=r'C:\Users\FAS\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\pdftoppm.exe'
for key,n in [('doc2',53),('doc5',113),('doc5',174),('doc5',238),('doc1',3)]:
 f=next(x for x in m if x['key']==key)
 subprocess.run([exe,'-f',str(n),'-l',str(n),'-scale-to','1600','-png','-singlefile',f['path'],str(p/f'source_{key}_{n}')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
