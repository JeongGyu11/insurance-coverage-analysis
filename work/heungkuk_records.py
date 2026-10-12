from pathlib import Path
import json,re,difflib
from datetime import datetime,timezone,timedelta
R=Path('work/heungkuk');M=json.loads((R/'manifest.json').read_text(encoding='utf8'));S=json.loads((R/'sections.json').read_text(encoding='utf8'));T=json.loads((R/'table_rows.json').read_text(encoding='utf8'))
def co(s):return re.sub(r'\s+','',s or '')
def clean(s):
 s=re.sub(r'\s+',' ',s or '').strip()
 for term in ['피보험자','보험가입금액','보험기간','진단확정','보장개시일','특별약관','후유장해','장해지급률','직접적인','최초','상급종합병원','요양병원','기타피부암','갑상선암','제자리암','경계성종양','통합간편가입형','건강고지형','자기부담금','보상한도','연간','수술분류표','신재진단암']:
  s=re.sub(r'\s*'.join(term),term,s)
 return s
def norm(s):
 s=co(s).replace('보험료납입면제대상보장','보험료납입면제대상');s=re.sub(r'\((?:간편가입|통합간편가입형|건강고지형)\)','',s);s=s.removeprefix('질병질병').join(['질병','']) if s.startswith('질병질병') else s
 return re.sub(r'^\d+(?:-\d+)?\.','',s).replace('특별약관','').replace('·','ㆍ')
B=[];issues=[]
for x in T:
 x=dict(x);x['name']=re.sub(r'^(?:기\s*본\s*계\s*약|의\s*무\s*가\s*입|상\s+해|질\s+병|비\s*용\s*손\s*해)\s+','',x['name']);x['end_page']=x['page']
 if not x['name']:
  if B and B[-1]['doc']==x['doc']:
   B[-1]['cause']+=' '+x['cause'];B[-1]['amount']+=' '+x['amount'];B[-1]['end_page']=x['page']
  continue
 if not x['amount'] and B and B[-1]['doc']==x['doc'] and x['page']>B[-1]['end_page']:
  B[-1]['name']+=x['name'];B[-1]['cause']+=' '+x['cause'];B[-1]['end_page']=x['page'];continue
 if not x['amount'] and B and B[-1]['doc']==x['doc']:x['amount']=B[-1]['amount']
 if not x['cause'] and B and B[-1]['doc']==x['doc']:
  B[-1]['amount']+=' '+x['name']+' '+x['amount'];continue
 if not x['amount'] or not x['cause']:issues.append(x);continue
 x['name']=co(x['name']);B.append(x)
(R/'benefits.json').write_text(json.dumps(B,ensure_ascii=False,indent=2),encoding='utf8')
exact={k:{norm(v):sec for sec in secs for v in sec['aliases']} for k,secs in S.items()};records=[];links=[];stamp=datetime.now(timezone(timedelta(hours=9))).isoformat(sep=' ',timespec='seconds')
def add(di,name,target,amount,cond,ps,pe,summary,summarypg,score=1,raw=None):
 prod=re.sub(r'^販売完了__','',M[di]['product']);prod=re.sub(r'^販売.*','',prod) if prod.startswith('販売') else re.sub(r'^판매완료__\d+_','',prod).replace('_',' ')
 records.append(dict(id=len(records)+1,company_name='흥국화재',product_name=prod,coverage_name=name,coverage_target=target,coverage_amount=amount,coverage_conditions=cond,created_at=stamp,updated_at=stamp,source_file=M[di]['path'],source_page=f'{ps}–{pe}',summary_file=M[summary]['path'] if summary is not None else '',summary_page=summarypg,review=f'상품요약서 지급표와 개별 약관 연결(제목 대조 {score:.3f}).',raw=raw))
def concise(s):
 s=clean(s)
 s=re.sub(r'제\s*\d+조(?:의\d+)?\s*\([^()]*(?:\([^()]*\)[^()]*)*\)(?:\s*제\d+항)?','',s)
 s=re.sub(r'제\d+항(?:에서 정한|에 따른|의 경우)?','',s)
 s=re.sub(r'\(이하[^)]*\)','',s)
 return re.sub(r'\s+',' ',s).strip(' .')
for b in B:
 di=b['doc']+1;n=norm(b['name']);candidates=[]
 for sec in ([exact[str(di)][n]] if n in exact[str(di)] else S[str(di)]):
  vals=[norm(v) for v in sec['aliases']];score=max((difflib.SequenceMatcher(None,n,v).ratio() for v in vals),default=0)
  if n in vals:score=1
  candidates.append((score,sec))
 score,sec=max(candidates,key=lambda v:v[0])
 if score<.78:links.append(dict(doc=di,name=b['name'],page=b['page'],score=score,candidate=sec['name']))
 event=clean(b['cause']);rawamount=clean(b['amount']);name=b['name'];limits=[]
 for v in re.findall(r'\([^)]*(?:1회|회한|한도|미만|년후|진단후|년이상|일이상)[^)]*\)',event+' '+rawamount):limits.append(concise(v).strip('()')+'.')
 target=re.sub(r'\([^)]*(?:1회|회한|한도|미만)[^)]*\)','',event);target=re.split(r'주\)|※',target)[0].strip()
 target='피보험자가 '+target
 amount='보험증권에 정한 해당 담보 가입금액을 기준으로 '+rawamount.replace('가입금액','가입금액')+'를 지급합니다. 금액은 계약별 가입금액·세부보장 금액에 따라 결정됩니다.'
 if '×장해지급률' in co(rawamount):amount='해당 담보 가입금액 × 장해분류표의 해당 장해지급률. '+rawamount+'이며 실제 원화 지급액은 계약의 가입금액과 판정 지급률로 계산합니다.'
 if '종별가입금액' in co(rawamount):amount='해당 수술·시술의 종별 세부보장에 약정한 가입금액. 종별 가입금액이 다를 수 있으므로 실제 계약의 세부보장 금액을 적용합니다. '+rawamount
 cond=limits[:];extra_targets=[]
 if score>=.78:
  for a in sec['articles']:
   title=co(a['title']);text=a['text']
   if not any(v in title for v in ['지급사유','세부규정','보장개시','지급하지','보상하지','정의','한도','공제']):continue
   blocks=re.split(r'[①-⑳㉑-㉟]',text)
   for block in blocks:
    compact=co(block)
    if len(compact)<10 or any(v in compact for v in ['제3자','합의하지못','연명의료','계약자적립액','보험수익자지정','정의는아래와같','의료기관)의료기관','금융위원회','관련법령등의개정']):continue
    if '정의' in title and not any(v in compact for v in ['제외','허가','승인','암보장','90일','1년','보험금지급']):continue
    if not any(v in compact for v in ['한도','연간','최초','지급하지','보상하지','공제','면책','감액','보장개시일','중복','동일한','차감','제외','허가','승인','50%','365일','180일','90일','1년']):continue
    q=concise(block)
    q=re.split(r'예시|용어의 정의|용어풀이|【별표',q)[0]
    sentences=re.split(r'(?<=다\.)\s+',q)
    useful=[v for v in sentences if not any(z in co(v) for z in ['제3자','분쟁','청구서','다음각호의어느하나','법률이개정','별도로정한방법','계약자가변경','알려드립니다'])]
    q=' '.join(useful)
    if q:cond.append(q.rstrip('.')+'.')
 cond=list(dict.fromkeys(cond))
 # remove table/header examples and repeated grant event from conditions
 cond=[q for q in cond if len(q)<2400]
 if '납입면제대상' in n:amount='해당 특별약관 가입금액을 최초 지급사유 발생 시 지급하는 정액 보장. 상품요약서는 지급금액을 가입금액으로 표시합니다. 보험료 납입면제 제도 자체와 이 담보의 현금 보험금을 구분합니다.'
 if '감액없음' in name:cond.append('이 담보는 명시된 감액 없는 지급형으로, 초기 50% 감액을 적용하지 않습니다.')
 if '면책없음' in name:cond.append('이 담보는 명시된 면책 없는 지급형으로 암 90일 면책을 적용하지 않습니다.')
 if not cond:cond=['보험기간 중 위 보장대상 사고·질환의 지급사유가 발생한 경우 지급합니다.']
 add(di,name,target,amount,' '.join(cond),sec['start'] if score>=.78 else 1,sec['end'] if score>=.78 else M[di]['pages'],b['doc'],str(b['page']) if b['end_page']==b['page'] else f'{b["page"]}–{b["end_page"]}',score,b)
# attach mature analysis data and source-match diagnostics
(R/'records_base.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8');(R/'link_issues.json').write_text(json.dumps(links,ensure_ascii=False,indent=2),encoding='utf8');(R/'table_issues.json').write_text(json.dumps(issues,ensure_ascii=False,indent=2),encoding='utf8')
print('BENEFITS',len(B),'LINK ISSUES',len(links),'TABLE ISSUES',len(issues));print(links[:25])


