from pathlib import Path
import json,re
from datetime import datetime,timezone,timedelta
out=Path('work/db');m=json.loads((out/'manifest.json').read_text(encoding='utf8'));tabs=json.loads((out/'cells.json').read_text(encoding='utf8'))
def tidy(t):return re.sub(r'\s+',' ',str(t or '').replace('\x00',' ')).strip()
def comp(t):return re.sub(r'\s','',str(t or '').replace('\x00',''))
plans=[{'key':'doc1','page':55,'start':28,'product':'무배당 백년친구 생활보험(2507)','type':'1종(레저보장형)'},{'key':'doc1','page':121,'start':93,'product':'무배당 백년친구 생활보험(2507)','type':'2종(건강보장형)'},{'key':'doc3','page':46,'start':21,'product':'무배당 생활안심보험(2507)','type':'주계약'}]
rec=[];now=datetime.now(timezone(timedelta(hours=9))).isoformat(timespec='seconds').replace('T',' ')
for plan in plans:
 pp=json.loads((out/(plan['key']+'.json')).read_text(encoding='utf8'));source=next(f for f in m if f['key']==plan['key']);body='\n'.join(t.replace('\x00',' ') for t in pp[plan['start']-1:plan['page']-1]);ms=list(re.finditer(r'(?m)^제\s*\d+조(?:의\d+)?\s*【([^】]+)】',body));articles=[]
 for j,a in enumerate(ms):
  text=tidy(body[a.end():ms[j+1].start() if j+1<len(ms) else len(body)]);articles.append((tidy(a.group(1)),text))
 common=next((text for name,text in articles if '지급하지' in name),'')
 ptab=next(t for t in tabs if t['key']==plan['key'] and t['page']==plan['page']);text=ptab['text'].replace('\x00',' ')
 notes=text[text.index('주)'):] if '주)' in text else text[text.index('※'):] if '※' in text else ''
 notes=re.sub(r'\n(?:\d+\s*|\(무\).*?)$','',notes.strip())
 for row in ptab['tables'][0]['rows'][1:]:
  name=re.sub(r'\(제\d+조.*','',row[0].replace('\n','').replace('\x00',' ')).strip();cause=tidy(row[1]);amount='[보험가입금액 1,000만원 기준] '+tidy(row[2])
  if '대상포진' in name or '통풍' in name:amount+='; 계약일부터 1년 미만 진단확정 시 해당 진단자금의 50% 지급'
  extra=[]
  if '1종' in plan['type'] and ('아킬레스' in name or '무릎' in name):extra.append('재해수술급여금에 추가로 지급하며, 해당 질환의 직접적인 치료를 목적으로 수술을 받은 경우에 한함.')
  if '재해골절' in name:extra.append('치아파절 제외. 동일한 재해의 복합골절은 1회만 지급. 의학적 처치·치료 목적으로 골절을 시킨 경우 지급하지 않음.')
  if plan['key']=='doc3' and ('아킬레스' in name or '무릎' in name):extra.append('재해수술급여금에 추가로 지급하며, 해당 질환의 직접적인 치료를 목적으로 수술을 받은 경우에 한함.')
  if '연간' in amount:extra.append('연간은 계약일부터 매 1년 단위로 도래하는 계약해당일 전일까지의 기간(해당일이 없으면 해당 월 마지막 날).')
  if '장해' in name:
   for an,at in articles:
    if '세부규정' in an:
     extra.extend(p for p in re.split(r'(?=[①-⑳])',at) if any(s in comp(p) for s in ['장해상태가영구','한시장해','동일한신체부위','이미지급','동일한재해','180일']) and '장해' in p)
  if '수술' in name:
   for an,at in articles:
    if '수술' in an and '정의' in an:extra.extend(p for p in re.split(r'(?=[①-⑳])',at) if '제외' in p)
  target='피보험자(가입나이·보험기간 및 인수한도는 사업방법서와 계약별 기준)'
  cond='\n'.join(x for x in [cause,*extra,('보험금 지급 제외: '+common) if common else ''] if x)
  rec.append({'id':len(rec)+1,'company_name':'DB생명','product_name':plan['product'],'coverage_name':name+' ['+plan['type']+']','coverage_target':target,'coverage_amount':amount,'coverage_conditions':cond,'created_at':now,'updated_at':now,'type':plan['type'],'source_file':source['path'],'source_page':plan['page'],'article_pages':f"{plan['start']}–{plan['page']-1}",'duplicate_paths':source['duplicate_paths'],'review':'e-생활보험 폴더의 문서도 백년친구 생활보험과 동일(SHA-256 일치); 원문 상품명으로 통합' if plan['key']=='doc1' else '약관_2.pdf는 법·규정 부록으로 담보 생성에서 제외','table_notes':tidy(notes)})
(out/'records.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf8')
print('rows',len(rec),'counts',[sum(r['type']==p['type'] and r['product_name']==p['product'] for r in rec) for p in plans]);print('max conditions',max(len(r['coverage_conditions']) for r in rec));print([(n,len(t)) for n,t in articles if '지급하지' in n])
