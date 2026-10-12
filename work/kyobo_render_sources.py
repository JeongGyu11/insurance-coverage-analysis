import json,subprocess
from pathlib import Path
p=Path('work/kyobo');m=json.loads((p/'manifest.json').read_text(encoding='utf8'));exe=r'C:\Users\FAS\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\pdftoppm.exe'
for key,n in [('doc3',76),('doc5',1604),('doc7',59),('doc3',890)]:
 f=next(x for x in m if x['key']==key)
 subprocess.run([exe,'-f',str(n),'-l',str(n),'-scale-to','1600','-png','-singlefile',f['path'],str(p/f'source_{key}_{n}')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
