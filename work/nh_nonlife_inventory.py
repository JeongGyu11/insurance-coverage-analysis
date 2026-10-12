from pathlib import Path
from zipfile import ZipFile
import hashlib,json
root=Path(r'C:\Users\FAS\Desktop\데이터분석\NH농협손해보험_2507');out=Path('work/nh_nonlife');out.mkdir(exist_ok=True)
files=[]
for f in sorted(root.rglob('*')):
 if not f.is_file():continue
 h=hashlib.sha256(f.read_bytes()).hexdigest();entry={'path':str(f),'product_folder':f.parent.name,'kind':f.stem,'hash':h,'size':f.stat().st_size};files.append(entry)
 if f.suffix.lower()=='.zip':
  members=[]
  with ZipFile(f) as z:
   for n,info in enumerate(z.infolist()):
    if info.is_dir():continue
    data=z.read(info);mh=hashlib.sha256(data).hexdigest();target=out/(mh+Path(info.filename).suffix.lower());target.write_bytes(data)
    members.append({'member':info.filename,'path':str(target.resolve()),'hash':mh,'size':len(data)})
  entry['members']=members
(out/'inventory.json').write_text(json.dumps(files,ensure_ascii=False,indent=2),encoding='utf8')
print('Files',len(files),'Folders',len(set(x['product_folder'] for x in files)))

