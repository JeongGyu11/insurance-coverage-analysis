import json,re
from pathlib import Path
p=Path('work/kyobo');r=json.loads((p/'records.json').read_text(encoding='utf8'));s=json.loads((p/'sections.json').read_text(encoding='utf8'))
print('max conditions',max(len(x['coverage_conditions']) for x in r));print('uncovered sections')
for k,v in s.items():
 for x in v:
  if not any(z['source_name']==re.sub(r'\s+','',x['name']) for z in r) and '주계약' not in x['name']:print(k,x['start'],x['name'])
print('term benefits')
for x in r:
 if '간편경영인' in x['product_name']:print(x['coverage_name'],x['source_page'],x['coverage_amount'][:300])
print('possible odd names')
for x in r:
 if any(z in x['coverage_name'] for z in ['험금험','교보교보','생금','연부','제1','"']):print(x['id'],x['coverage_name'])
assert len({(x['product_name'],x['coverage_name']) for x in r})==len(r)
