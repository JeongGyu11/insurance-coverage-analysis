import zipfile,json,re
from pathlib import Path
from lxml import etree as E
p=Path('C:/Users/FAS/Desktop/데이터분석/AIG손해보험_2507_담보분석.xlsx');ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def read(path):
 with zipfile.ZipFile(path) as z:
  ss=[''.join(x.itertext()) for x in E.fromstring(z.read('xl/sharedStrings.xml'))];out=[]
  for i in range(1,4):
   d={}
   for c in E.fromstring(z.read(f'xl/worksheets/sheet{i}.xml')).findall('.//s:sheetData/s:row/s:c',ns):
    v=c.find('s:v',ns);v=v.text if v is not None else ''
    if c.get('t')=='s':v=ss[int(v)]
    elif c.get('t')=='inlineStr':v=''.join(c.find('s:is',ns).itertext())
    d[c.get('r')]=v
   out.append(d)
  return out
if __name__=='__main__':
 d=read(p);changes=[]
 for cell,s in d[0].items():
  if not cell.startswith('G') or cell=='G1':continue
  new=re.sub(r'해당\s*특약을\s*가입한\s*계약에\s*적용합니다\.[ \t]*','',s).strip()
  if new!=s:changes.append({'cell':cell,'old':s,'new':new})
 Path('work/aig_phrase').mkdir(exist_ok=True)
 Path('work/aig_phrase/changes.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2),encoding='utf8')
 Path('work/aig_phrase/before.json').write_text(json.dumps(d,ensure_ascii=False),encoding='utf8')
 print('MATCHES',len(changes));print(json.dumps(changes[:2],ensure_ascii=False))
 print('similar',[(c,s[:180]) for c,s in d[0].items() if c.startswith('G') and ('가입한 계약' in s or '가입된 계약' in s)][:8])


