import json,subprocess,concurrent.futures
from pathlib import Path
m=json.loads(Path('work/mirae/manifest.json').read_text(encoding='utf8'))
base=Path('work/mirae').resolve()
def run(f):
 p=base/f['key'];p.mkdir(exist_ok=True)
 images=list(p.glob('page-*.png'))
 if len(images)!=f['pages']:
  subprocess.run(['pdftoppm','-scale-to','1800','-png',f['path'],str(p/'page')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 print('RENDERED',f['key'],f['pages'],flush=True)
 command="& ([scriptblock]::Create([System.IO.File]::ReadAllText('"+str(Path('work/mirae_ocr.ps1').resolve()).replace('\\','/')+"'))) -InputDir '"+str(p).replace('\\','/')+"'"
 subprocess.run(['powershell.exe','-NoProfile','-Command',command],check=True,stdout=subprocess.DEVNULL)
 texts=[x.read_text(encoding='utf-8-sig') for x in sorted(p.glob('page-*.png.ocr.txt'))]
 assert len(texts)==f['pages'],(f['key'],len(texts))
 (base/(f['key']+'_ocr.json')).write_text(json.dumps(texts,ensure_ascii=False),encoding='utf8')
 (base/(f['key']+'_ocr.txt')).write_text('\n'.join('=== PAGE '+str(i+1)+' ===\n'+t for i,t in enumerate(texts)),encoding='utf8')
 print('OCR COMPLETE',f['key'],len(texts),flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:list(ex.map(run,sorted(m,key=lambda x:(x['kind']=='약관',x['pages']))))
