import fs from 'node:fs/promises';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const root='work/hyundai',r=JSON.parse(await fs.readFile(root+'/records.json','utf8')),m=JSON.parse(await fs.readFile(root+'/manifest.json','utf8')),pending=r.filter(x=>x.review.includes('추가 대조'));
const w=Workbook.create(),d=w.worksheets.add('담보데이터'),s=w.worksheets.add('처리현황'),p=w.worksheets.add('출처·검토'),v=w.worksheets.add('추가대조');
const h=['id','company_name','product_name','coverage_name','coverage_target','coverage_amount','coverage_conditions','created_at','updated_at'];
function setup(sh,vals,widths,name){sh.getRangeByIndexes(0,0,vals.length,widths.length).values=vals;sh.showGridLines=false;const a=sh.getRangeByIndexes(0,0,vals.length,widths.length);a.format.font={name:'Malgun Gothic',size:10};a.format.wrapText=true;a.format.verticalAlignment='top';a.format.rowHeight=100;widths.forEach((x,i)=>sh.getRangeByIndexes(0,i,vals.length,1).format.columnWidth=x);sh.getRangeByIndexes(0,0,1,widths.length).format={fill:'#153957',font:{name:'Malgun Gothic',size:10,bold:true,color:'#FFFFFF'},rowHeight:32,wrapText:true};if(name)sh.tables.add(sh.getRangeByIndexes(0,0,vals.length,widths.length),true,name);sh.freezePanes.freezeRows(1);}
setup(d,[h,...r.map(x=>h.map(k=>x[k]))],[8,18,58,82,90,105,115,29,29],'HyundaiCoverages');
d.freezePanes.freezeColumns(2);d.getRange('H2:I'+(r.length+1)).setNumberFormat('@');
for(let i=0;i<r.length;i++){const x=r[i];d.getRangeByIndexes(i+1,0,1,9).format.rowHeight=Math.min(409,Math.max(85,Math.ceil(Math.max(x.coverage_name.length/46,x.coverage_target.length/51,x.coverage_amount.length/60,x.coverage_conditions.length/66))*18+25));if(x.review.includes('추가 대조'))d.getRangeByIndexes(i+1,3,1,1).format.fill='#FFF2CC';}
const products=[...new Set(m.map(x=>x.product))];
const vals=[['분석 항목','내용','담보 행 수','처리·검토'],
['총계','47개 상품 폴더 / 137개 PDF',r.length,'45개 담보 상품; 제도성 폴더 2개는 독립 지급담보 없음.'],
['약관 조문 추가 대조','노란색 담보명 및 추가대조 시트',pending.length,'요약서 지급표는 확보했으나 같은 제목의 약관 조문 연결이 확정되지 않음. DB 적재 전 검토 필요.'],
['정리 기준','DB 예시의 9개 컬럼',null,'보장대상: 사람·질환·치료 범위. 금액: 가입금액·비율·산식·한도·단위. 조건: 개시·감액·횟수·기간·자기부담·핵심 제외.'],
['원본 버전','현대해상_2507 폴더 자료',null,'원본에 표기된 Hi2504·2505·2507·2508 등 버전을 상품명에 유지. 파일명만으로 시행일을 변경하지 않음.'],
['중복·제도','동일 지급구조 중복 제외',null,'할인·중지/재개·위험 제외만 규정하는 제도는 별도 보험금 담보로 만들지 않음.'],
['출처 기준','실제 PDF 페이지',null,'약관 페이지 미확정 항목은 빈칸. 상품요약서 지급표 페이지와 원본 파일 경로로 확인.'],
['일시·번호','한국시간 +09:00 텍스트',null,'id는 이 파일 내 연속번호. DB 저장 시 생성일시·수정일시 및 기본키는 DB 정책에 맞춰 처리.'],
['조건 요약','핵심 지급요건 중심',null,'일반 가입 안내·청구 절차는 반복하지 않음. 전체 면책·정의·분류표는 원문 확인.'],
...products.map(n=>{const clean=n.replace(/^판매완료__\d+_/,'').replaceAll('_',' ');return[n,clean,r.filter(x=>x.product_name===clean).length,r.some(x=>x.product_name===clean&&x.review.includes('추가 대조'))?'추가대조 항목 있음':r.some(x=>x.product_name===clean)?'지급담보 정리':'제도성 자료: 독립 지급담보 미생성'];}),
['원본 파일','문서 종류 / PDF 페이지',null,'SHA-256'],
...m.map(x=>[x.path,x.kind+' / '+x.pages,null,x.sha256])];
setup(s,vals,[100,64,15,110],null);
const ph=['id','상품명','담보명','약관 파일','약관 PDF 페이지','요약서 파일','요약서 PDF 페이지','검토'];
const src=x=>[x.id,x.product_name,x.coverage_name,x.source_file,x.source_page,x.summary_file,x.summary_page,x.review];
setup(p,[ph,...r.map(src)],[8,58,82,115,20,115,20,95],'HyundaiSources');
setup(v,[ph,...pending.map(src)],[8,58,82,115,20,115,20,95],'HyundaiPending');
w.recalculate();
console.log((await w.inspect({kind:'table',range:'처리현황!A1:D9',include:'values',tableMaxRows:9,tableMaxCols:4,maxChars:2100})).ndjson);
for(const [sheetName,range,name] of [['처리현황','A1:D3','summary'],['담보데이터','E2:G3','coverage'],['출처·검토','A1:C3','sources'],['추가대조','A1:C3','pending']]){
const b=await w.render({sheetName,range,scale:1,format:'png'});await fs.writeFile(root+'/'+name+'_preview.png',new Uint8Array(await b.arrayBuffer()));}
await fs.mkdir('outputs/01a10ed0-eb0e-7720-80fe-23aace7c950b',{recursive:true});
await(await SpreadsheetFile.exportXlsx(w)).save('outputs/01a10ed0-eb0e-7720-80fe-23aace7c950b/현대해상_2507_담보분석.xlsx');console.log('SAVED',r.length,pending.length);

