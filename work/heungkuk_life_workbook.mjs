import fs from 'node:fs/promises';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const root='work/heungkuk_life',r=JSON.parse(await fs.readFile(root+'/records.json','utf8')),m=JSON.parse(await fs.readFile(root+'/manifest.json','utf8'));
const w=Workbook.create(),d=w.worksheets.add('담보데이터'),s=w.worksheets.add('처리현황'),p=w.worksheets.add('출처·검토'),last=r.length+1;
const h=['id','company_name','product_name','coverage_name','coverage_target','coverage_amount','coverage_conditions','created_at','updated_at'];
function style(sh,n,widths){sh.showGridLines=false;const a=sh.getRangeByIndexes(0,0,n,widths.length);a.format.font={name:'Malgun Gothic',size:10};a.format.wrapText=true;a.format.verticalAlignment='top';widths.forEach((v,c)=>sh.getRangeByIndexes(0,c,n,1).format.columnWidth=v);}
function head(sh,range){sh.getRange(range).format={fill:'#153957',font:{name:'Malgun Gothic',size:10,bold:true,color:'#FFFFFF'},rowHeight:32,wrapText:true};}
d.getRange('A1:I'+last).values=[h,...r.map(x=>h.map(k=>x[k]))];style(d,last,[8,18,54,76,88,100,115,29,29]);head(d,'A1:I1');d.tabColor='#153957';d.tables.add('A1:I'+last,true,'HeungkukLifeCoverages');d.freezePanes.freezeRows(1);d.freezePanes.freezeColumns(2);d.getRange('H2:I'+last).setNumberFormat('@');
r.forEach((x,i)=>d.getRange('A'+(i+2)+':I'+(i+2)).format.rowHeight=Math.min(409,Math.max(90,Math.ceil(Math.max(x.coverage_name.length/43,x.coverage_target.length/50,x.coverage_amount.length/57,x.coverage_conditions.length/66))*18+25)));
style(s,32,[64,18,27,91]);s.getRange('A2').values=[['흥국생명 2025년 7월 담보 분석']];s.getRange('A2').format.font={name:'Malgun Gothic',size:14,bold:true,color:'#153957'};
const products=[...new Set(r.map(x=>x.product_name))];
s.getRange('A4:D7').values=[['상품명','담보 행 수','분석 범위','특징'],...products.map((n,i)=>[n,r.filter(x=>x.product_name===n).length,'주계약·지급특약·납입면제',i===0?'생활자금집중형·사망보장강화형의 사망금액과 보증지급 횟수를 구분.':i===1?'특약 69개를 대조. 수술 1~5종, 통합암 10종, 기본형·바로보장형 및 최초·갱신계약 구분.':'치매 CDR·장기요양 등급·실제 급여 이용을 구분. 현물 프로그램, 생활자금, 시설입소·홈케어도 포함.'])];head(s,'A4:D4');s.getRange('A5:D7').format.rowHeight=86;
s.getRange('A9:B11').values=[['총 담보 행 수',r.length],['원본 상품 폴더 / PDF 수','4 / 8'],['중복 제외 후 상품 / PDF 수','3 / 6']];s.getRange('A9:B11').format.rowHeight=30;
s.getRange('A13:D21').values=[['원본 폴더','문서 종류','PDF 페이지','처리'],...m.map(x=>[x.product,x.kind,x.pages,x.key==='doc6'||x.key==='doc7'?'row01 파일과 SHA-256 동일. 담보 중복 제외.':'분석 반영'])];head(s,'A13:D13');s.getRange('A14:D21').format.rowHeight=80;
const notes=[
'DB 예시와 동일한 9개 컬럼 순서를 유지했습니다. 담보별 보장대상에는 사람·질환·치료·기관·등급 범위를, 금액에는 가입금액 기준·비율·산식·지급단위를 설명했습니다.',
'지급표의 기준 가입금액으로 표시된 예시는 실제 고정 보장금액으로 취급하지 않습니다. 실제 계약 가입금액과 가입형에 따라 계산합니다. 최초계약 감액과 갱신계약 지급표는 구분했습니다.',
'조건은 보장개시·감액·지급 횟수·기간·중복지급·제외·실제 이용요건을 중심으로 정리했습니다. “해당 특약을 가입한 계약에 적용합니다.” 등의 일반 가입 안내와 청구·분쟁 절차는 반복하지 않았습니다.',
'치매담은시니어보장보험 row01·row02의 약관과 사업방법서는 각각 동일한 SHA-256 값입니다. 같은 상품·담보를 중복 생성하지 않고 row01을 대표 출처로 사용했습니다.',
'보험료 납입면제는 현금 보험금과 구분했습니다. 지정대리청구·인수조건 등 독립 보험금 지급사유가 없는 제도성 특약, 해약환급금 및 공통 장해분류표는 별도 담보로 중복 작성하지 않았습니다.',
'출처·검토 시트의 id로 해당 약관과 실제 PDF 페이지를 찾을 수 있습니다. 약관 인쇄 페이지는 PDF 페이지보다 2쪽 큽니다. 생성·수정일시는 +09:00 포함 텍스트이며 id는 이 파일 내 연속번호입니다.'
];s.getRange('A24:A29').values=notes.map(v=>[v]);notes.forEach((v,i)=>{s.getRange('A'+(i+24)+':D'+(i+24)).merge();s.getRange('A'+(i+24)+':D'+(i+24)).format.rowHeight=Math.ceil(v.length/105)*19+28;});
const ph=['id','상품명','담보명','약관 파일','실제 PDF 페이지','사업방법서 파일','사업방법서 페이지','검토내용'];
p.getRange('A1:H'+last).values=[ph,...r.map(x=>[x.id,x.product_name,x.coverage_name,x.source_file,x.source_page,x.business_file,x.business_page,x.review])];style(p,last,[8,54,76,115,22,115,20,77]);head(p,'A1:H1');p.getRange('A2:H'+last).format.rowHeight=100;p.tables.add('A1:H'+last,true,'HeungkukLifeSources');p.freezePanes.freezeRows(1);
w.recalculate();console.log((await w.inspect({kind:'table',range:'처리현황!A4:D11',include:'values',tableMaxRows:8,tableMaxCols:4,maxChars:1700})).ndjson);
console.log((await w.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!',options:{useRegex:true,maxResults:10},maxChars:400})).ndjson);
for(const [sheetName,range,name] of [['처리현황','A4:D11','summary'],['담보데이터','E120:G121','care'],['出처·검토'.replace('出','출'),'A1:C3','source']]){
const b=await w.render({sheetName,range,scale:1,format:'png'});await fs.writeFile(root+'/'+name+'_preview.png',new Uint8Array(await b.arrayBuffer()));
}
await fs.mkdir('outputs/01a10ed0-eb0e-7720-80fe-23aace7c950b',{recursive:true});
await(await SpreadsheetFile.exportXlsx(w)).save('outputs/01a10ed0-eb0e-7720-80fe-23aace7c950b/흥국생명_2507_담보분석.xlsx');console.log('SAVED',r.length);

