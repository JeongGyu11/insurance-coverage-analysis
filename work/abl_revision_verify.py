import json,re,zipfile
from pathlib import Path
from lxml import etree as E
NS={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def read(p):
 with zipfile.ZipFile(p) as z:
  ss=[]
  if 'xl/sharedStrings.xml' in z.namelist():
   ss=[''.join(x.itertext()) for x in E.fromstring(z.read('xl/sharedStrings.xml'))]
  data=[]
  for i in range(1,4):
   root=E.fromstring(z.read(f'xl/worksheets/sheet{i}.xml'));cells={}
   for c in root.findall('.//s:sheetData/s:row/s:c',NS):
    v=c.find('s:v',NS);v=v.text if v is not None else ''
    if c.get('t')=='s':v=ss[int(v)]
    elif c.get('t')=='inlineStr':v=''.join(c.find('s:is',NS).itertext())
    cells[c.get('r')]=v
   data.append(cells)
  return data
a=read('work/abl_revision/original.xlsx');b=read('outputs/01a10ed0-eb0e-7720-80fe-23aace7c950b/ABL생명_2507_담보분석.xlsx')
assert [b[0].get(f'{c}1') for c in 'ABCDEFGHI']==['id','company_name','product_name','coverage_name','coverage_target','coverage_amount','coverage_conditions','created_at','updated_at']
for row in range(2,652):
 for c in 'ABCDH':assert a[0][f'{c}{row}']==b[0][f'{c}{row}'],(c,row)
 for c in 'EFGI':assert b[0][f'{c}{row}']
 for c in 'ABCDEG':assert a[2][f'{c}{row}']==b[2][f'{c}{row}'],('source',c,row)
assert len([k for k in b[0] if re.fullmatch(r'A\d+',k)])==651
old=json.loads(Path('work/records.json').read_text(encoding='utf8'));new=json.loads(Path('work/abl_revision/revised.json').read_text(encoding='utf8'))
missing=[]
for x,y in zip(old,new):
 tokens=re.findall(r'(?:US\$\s*)?[\d,]+(?:\.\d+)?\s*(?:만원|달러|%)',x['amount'])
 for token in tokens:
  if re.sub(r'\s+','',token) not in re.sub(r'\s+','',y['amount_display']):missing.append((x['id'],token))
assert not missing,missing
assert '1일 이상' in new[78]['target']
assert '요양병원' in new[78]['conditions_display'] and '제외' in new[321]['conditions_display']
assert '중증 이외의 갑상선암' in new[317]['conditions_display']
assert '1년' not in new[605]['conditions_display']
assert '추가 지급' in new[58]['conditions_display']
assert '450만원' in new[279]['amount_display'] and '1년 미만' in new[279]['amount_display']
assert new[280]['target']!=old[280]['target'] and '표적항암약물허가치료' in new[280]['target']
print('PASS: 650 rows; 9 headers; identity and created_at preserved; all original money/rate tokens retained; source identity preserved; representative exclusions, waiting periods and linked treatments checked.')
