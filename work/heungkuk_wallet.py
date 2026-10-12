import json,re,copy
from pathlib import Path
R=Path('work/heungkuk');r=json.loads((R/'records.json').read_text(encoding='utf8'));M=json.loads((R/'manifest.json').read_text(encoding='utf8'));S=json.loads((R/'sections.json').read_text(encoding='utf8'));T=json.loads((R/'table_rows.json').read_text(encoding='utf8'))
def co(s):return re.sub(r'\s+','',s or '')
out=[]
for x in r:
 if '플래티넘건강리셋월렛' in x['coverage_name']:continue
 if '잔고' in x['coverage_amount']:
  raw=x['raw'];orig=next((v for v in T if v['doc']==raw['doc'] and co(v['name'])==co(raw['name']) and v['page']==raw['page']),None)
  orig=orig or next((v for v in T if v['doc']==raw['doc'] and co(x['coverage_name']) in co(v['name']) and v['amount']),None);assert orig,x['id']
  x['coverage_target']='피보험자가 '+orig['cause'];x['coverage_amount']='해당 계약의 세부보장 가입금액을 지급합니다. 원문 지급표: '+orig['amount']+'.'
  x['coverage_conditions']=' '.join(v.strip('()')+'.' for v in re.findall(r'\([^)]*(?:회한|미만|한도)[^)]*\)',orig['cause']))
  x['summary_page']=str(orig['page']);x['review']+=' 월렛의 병합 지급표가 앞 담보에 붙은 부분을 분리하고 앞 담보의 원래 행으로 대조.'
 out.append(x)
wallets=0
for si in [24,27,30,33,36,39,42,45]:
 di=si+1;p=json.loads((R/f'doc{si}.json').read_text(encoding='utf8'));groups={}
 for j,t in enumerate(p):
  ct=co(t)
  if '구분지급사유지급금액' not in ct:continue
  for z in re.finditer(r'플래티넘건강리셋월렛\((3대질병고액치료,간병및상급병실입원(?:,상해사망)?)\)',ct):
   groups.setdefault(z[1],j+1)
 for group,page in groups.items():
  captions=[s for s in S[str(di)] if '플래티넘건강리셋월렛' in s['name'] and ('상해사망' in group)==('상해사망' in s['name'])]
  section=captions[0] if captions else None
  base=next(x for x in out if x['product_name']==re.sub(r'^판매완료__\d+_','',M[si]['product']).replace('_',' '))
  limit='가입금액 10억원에서 이미 지급한 이 월렛의 보험금 합계액을 차감한 잔고를 공동 한도로 합니다. 다른 세부보장을 받으면 남은 지급가능 금액도 줄어듭니다.'
  specs=[
   ('비급여 암수술비','암·기타피부암·갑상선암의 직접적인 치료를 목적으로 비급여(전액본인부담 포함) 암수술을 받은 경우.','수술 1회당 1,000만원','수술 회당 지급.'),
   ('비급여 항암방사선치료비','암·기타피부암·갑상선암을 직접 치료하기 위해 비급여(전액본인부담 포함) 항암방사선치료를 받은 경우.','연간 1회 5,000만원','연간 1회 한도.'),
   ('비급여 항암약물치료비(1~3기암·병기구분불가암)','1~3기암 또는 병기구분불가암으로 진단확정되고 직접 치료 목적의 비급여 항암약물치료를 받은 경우.','연간 1회 5,000만원','연간 1회 한도.'),
   ('비급여 항암약물치료비(4기암)','4기암으로 진단확정되고 직접 치료 목적의 비급여 항암약물치료를 받은 경우.','연간 1회 1억원','연간 1회 한도.'),
   ('비급여 2대질병수술비','뇌혈관질환·허혈성심질환으로 진단확정되고 직접 치료를 목적으로 비급여 수술을 받은 경우.','수술 1회당 1,000만원','수술 회당 지급.'),
   ('상급종합병원 1인실 질병입원비','질병 치료를 위해 상급종합병원 1인실(특실 포함)에 입원한 피보험자.','입원 1일당 30만원','1회 입원 30일 한도.'),
   ('상급종합병원 2~3인실 질병입원비','질병 치료를 위해 상급종합병원 2~3인실에 입원한 피보험자.','입원 1일당 5만원','1회 입원 30일 한도.'),
   ('종합병원 간병인사용 질병입원비','질병으로 종합병원에 계속입원하여 치료받으며 유상 간병인을 실제 사용한 피보험자.','사용일 1일당 15만원. 간병인 사용금액이 1일당 7만원 미만이면 지급금액의 50%.','1회 입원 사용일수 150일 한도. 실제 간병인 사용일만 지급.'),
   ('요양병원 간병인사용 질병입원비','질병으로 요양병원에 계속입원하여 치료받으며 유상 간병인을 실제 사용한 피보험자.','사용일 1일당 5만원','1회 입원 사용일수 150일 한도.'),
   ('간호·간병통합서비스사용 질병입원비','질병으로 계속입원하여 치료받으며 간호·간병통합서비스를 실제 사용한 피보험자.','사용일 1일당 7만원','1회 입원 사용일수 150일 한도.')
  ]
  if '상해사망' in group:specs.append(('일반상해사망','상해의 직접결과로 사망한 피보험자.','사망 지급사유 발생시점 월렛 잔고의 30%','상해사망형의 사망 지급구조이며 치료비 30% 지급이 아닙니다.'))
  sample=co(' '.join(p[page-1:page+3]));reduction='1년미만50%' in sample
  for j,(name,target,amount,conditions) in enumerate(specs):
   x=copy.deepcopy(base);x['coverage_name']='플래티넘 건강 리셋월렛('+group+') / '+name;x['coverage_target']=target;x['coverage_amount']=amount+'. '+limit;x['coverage_conditions']=conditions
   if reduction and j<5:x['coverage_conditions']+=' 최초계약일부터 1년 미만의 지급사유는 50% 감액하며 갱신계약에는 초기 감액을 다시 적용하지 않습니다.'
   if j<4:x['coverage_conditions']+=' 일반암 보장은 최초계약일(부활일) 포함 90일 경과 다음 날부터이며 기타피부암·갑상선암은 별도 보장개시 기준을 적용합니다.'
   x['summary_file']=M[si]['path'];x['summary_page']=f'{page}–{min(page+3,len(p))}';x['source_file']=M[di]['path'] if section else M[si]['path'];x['source_page']=f'{section["start"]}–{section["end"]}' if section else x['summary_page'];x['review']='페이지를 넘기는 월렛 병합 표를 세부 지급구조별로 분리. 개별 정액과 잔고 공동 한도 및 사망 30% 산식 구분.';x['raw']=None;x.pop('policy_file',None);out.append(x);wallets+=1
for i,x in enumerate(out,1):x['id']=i
(R/'records.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');(R/'pending_ids.json').write_text(json.dumps([x['id'] for x in out if x.get('policy_file')]),encoding='utf8')
print('ROWS',len(out),'WALLET',wallets,'GROUPS',groups)


