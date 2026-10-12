import sys,os,json
from pathlib import Path
sys.path.insert(0,str(Path('work/db_review_deps').resolve()))
import pg8000.native
c=pg8000.native.Connection(user='ga_rag',password=os.environ['TASK_DB_PASSWORD'],host='202.86.11.19',port=55432,database='ga_rag',timeout=20)
c.run('BEGIN READ ONLY');c.run("SET LOCAL statement_timeout='30s'");c.run("SET LOCAL lock_timeout='3s'")
out={}
def query(key,sql):
 rows=c.run(sql);names=[x['name'] for x in c.columns];out[key]=[dict(zip(names,r)) for r in rows]
query('connection',"SELECT current_database() AS database, current_user AS account, current_setting('transaction_read_only') AS read_only, version() AS version")
query('columns',"SELECT column_name,data_type,is_nullable,column_default FROM information_schema.columns WHERE table_schema='public' AND table_name='product_coverages' ORDER BY ordinal_position")
query('stats',"""SELECT count(*) AS rows,count(DISTINCT company_name) AS companies,count(DISTINCT (company_name,product_name)) AS products,
count(*) FILTER (WHERE nullif(btrim(coverage_target),'') IS NULL) AS target_blank,
count(*) FILTER (WHERE nullif(btrim(coverage_amount),'') IS NULL) AS amount_blank,
count(*) FILTER (WHERE nullif(btrim(coverage_conditions),'') IS NULL) AS conditions_blank,
round(avg(length(coverage_target)),1) AS target_avg,max(length(coverage_target)) AS target_max,
round(avg(length(coverage_amount)),1) AS amount_avg,max(length(coverage_amount)) AS amount_max,
round(avg(length(coverage_conditions)),1) AS conditions_avg,max(length(coverage_conditions)) AS conditions_max,
min(created_at)::text AS first_created,max(updated_at)::text AS last_updated FROM public.product_coverages""")
query('companies',"SELECT company_name,count(*) AS rows,count(DISTINCT product_name) AS products FROM public.product_coverages GROUP BY company_name ORDER BY count(*) DESC")
query('samples',"""WITH s AS (SELECT id,company_name,product_name,coverage_name,coverage_target,coverage_amount,coverage_conditions,
row_number() OVER (PARTITION BY company_name ORDER BY id) AS rn FROM public.product_coverages)
SELECT * FROM s WHERE rn<=4 ORDER BY company_name,id LIMIT 60""")
query('long_conditions',"SELECT id,company_name,product_name,coverage_name,coverage_target,coverage_amount,coverage_conditions FROM public.product_coverages ORDER BY length(coverage_conditions) DESC NULLS LAST LIMIT 8")
c.run('ROLLBACK');c.close()
p=Path('work/db_review');p.mkdir(exist_ok=True);(p/'inspection.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,default=str),encoding='utf8')
print(json.dumps(out,ensure_ascii=False,default=str))
