from pathlib import Path
import json,pdfplumber,re
p=Path('work/nh_nonlife');m=json.loads((p/'manifest.json').read_text(encoding='utf8'));out=[]
def comp(s):return re.sub(r'\s','',s or '')
for key,nums in [('doc1',range(9,15)),('doc5',range(8,11)),('doc8',range(5,10)),('doc11',range(1,6)),('doc14',range(47,70))]:
 f=next(x for x in m if x['key']==key)
 with pdfplumber.open(f['path']) as pdf:
  for n in nums:
   page=pdf.pages[n-1].dedupe_chars();tables=[]
   for t in page.find_tables():
    rows=t.extract();tables.append({'bbox':list(t.bbox),'rows':rows,'above':page.crop((max(0,t.bbox[0]-2),max(0,t.bbox[1]-100),min(page.width,t.bbox[2]+2),t.bbox[1])).extract_text() or ''})
   out.append({'key':key,'page':n,'text':page.extract_text() or '', 'tables':tables})
   page.close()
 print(key,len(nums),'pages',flush=True)
(p/'tables.json').write_text(json.dumps(out,ensure_ascii=False),encoding='utf8')
print('tables',sum(len(x['tables']) for x in out))
