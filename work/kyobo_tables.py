from pathlib import Path
import json,re,pdfplumber,sys
p=Path('work/kyobo');m=json.loads((p/'manifest.json').read_text(encoding='utf8'));plan=json.loads((p/'plan.json').read_text());out=[]
if '--additional' in sys.argv:
 out=json.loads((p/'tables.json').read_text(encoding='utf8'));present={(x['key'],x['page']) for x in out};extra=[]
 for q in plan:
  a=json.loads((p/(q['key']+'.json')).read_text(encoding='utf8'))
  missing=[i+1 for i,t in enumerate(a) if re.search(r'(급부명|급부명칭|구분|급여명).*지급사유.*지급(금액|내용|액)',re.sub(r'[ \t]','',t)) and (q['key'],i+1) not in present]
  if missing:extra.append({'key':q['key'],'pages':missing})
 plan=extra
if '--term' in sys.argv:
 out=[x for x in json.loads((p/'tables.json').read_text(encoding='utf8')) if x['key'] not in ['doc7','doc9']]
 plan=[q for q in plan if q['key'] in ['doc7','doc9']]
 for q in plan:q['pages'].extend([134,135,136] if q['key']=='doc7' else [151,152,153])
for q in plan:
 f=next(x for x in m if x['key']==q['key']);texts=json.loads((p/(q['key']+'.json')).read_text(encoding='utf8'))
 wanted=set()
 for n in q['pages']:
  wanted.add(n)
  for j in range(n,min(n+4,len(texts))):
   if re.search(r'보험금을\s*지급할\s*때의\s*적립이율|재해분류표|질병분류표',texts[j]):break
   wanted.add(j+1)
 with pdfplumber.open(f['path']) as pdf:
  for n in sorted(wanted):
   offset=1 if q['key'] in ['doc7','doc9'] else 0
   page=pdf.pages[n-1-offset].dedupe_chars();tabs=[]
   for t in page.find_tables():
    rows=t.extract();header=rows[0];norm=lambda x:re.sub(r'\s+','',x or '')
    causeidx=next((i for i,c in enumerate(header) if norm(c)=='지급사유'),None)
    amountidx=next((i for i,c in enumerate(header) if norm(c) in ['지급금액','지급내용','지급액']),None)
    fixed=[]
    if causeidx is not None and amountidx is not None:
     hc=t.rows[0].cells;cmid=(hc[causeidx][0]+hc[causeidx][2])/2;amid=(hc[amountidx][0]+hc[amountidx][2])/2
     for rr in t.rows[1:]:
      cc=next((c for c in rr.cells if c and c[0]<=cmid<c[2]),None)
      if not cc:continue
      ac=next((c for c in rr.cells if c and c[0]<=amid<c[2]),None);cx=cc[0];ax=ac[0] if ac else hc[amountidx][0];y0,y1=cc[1],cc[3]
      ranges=[(t.bbox[0],y0,cx,y1),(cx,y0,ax,y1),(ax,y0,t.bbox[2],y1)] if causeidx else [(cx,y0,ax,y1),(ax,y0,t.bbox[2],y1)]
      fixed.append([page.crop(b).extract_text() or '' for b in ranges])
    tabs.append({'bbox':list(t.bbox),'rows':rows,'fixed':fixed,'above':page.crop((0,max(0,t.bbox[1]-100),page.width,t.bbox[1])).extract_text() or ''})
   out.append({'key':q['key'],'page':n,'tables':tabs})
 (p/'tables.json').write_text(json.dumps(out,ensure_ascii=False),encoding='utf8')
 print(q['key'],len(wanted),flush=True)
