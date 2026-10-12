import fs from 'node:fs/promises';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const root='work/db',r=JSON.parse(await fs.readFile(`${root}/records.json`,'utf8'));
const w=Workbook.create(),d=w.worksheets.add('담보데이터'),s=w.worksheets.add('처리현황'),p=w.worksheets.add('출처·검토');
const h=['id','company_name','product_name','coverage_name','coverage_target','coverage_amount','coverage_conditions','created_at','updated_at'];
function style(sheet,n,widths){sheet.showGridLines=false;const a=sheet.getRangeByIndexes(0,0,n,widths.length);a.format.font={name:'Malgun Gothic',size:10};a.format.wrapText=true;a.format.verticalAlignment='top';widths.forEach((v,c)=>sheet.getRangeByIndexes(0,c,n,1).format.columnWidth=v);}
function head(sheet,range){sheet.getRange(range).format={fill:'#153957',font:{name:'Malgun Gothic',size:10,bold:true,color:'#FFFFFF'},rowHeight:32,wrapText:true};}
d.getRange('A1:I20').values=[h,...r.map(x=>h.map(k=>x[k]))];style(d,20,[8,15,45,55,55,70,150,30,30]);head(d,'A1:I1');d.tables.add('A1:I20',true,'DBCoverageData');d.freezePanes.freezeRows(1);d.freezePanes.freezeColumns(2);d.getRange('H2:I20').setNumberFormat('@');
r.forEach((x,i)=>d.getRange(`A${i+2}:I${i+2}`).format.rowHeight=Math.min(409,Math.max(110,x.coverage_conditions.split('\n').reduce((n,t)=>n+Math.ceil(t.length/100)+1,0)*15)));
style(s,25,[85,23,28]);s.getRange('A2').values=[['DB생명 상품공시 담보 분석']];s.getRange('A2').format.font={name:'Malgun Gothic',size:15,bold:true,color:'#153957'};
s.getRange('A4:C7').values=[['상품 / 종형','담보 행 수','지급표 PDF 페이지'],['백년친구 생활보험(2507) · 1종(레저보장형)',7,55],['백년친구 생활보험(2507) · 2종(건강보장형)',8,121],['생활안심보험(2507) · 주계약',4,46]];head(s,'A4:C4');s.getRange('A5:C7').format.rowHeight=36;
s.getRange('A9:B14').values=[['전체 담보 행 수',19],['원본 상품 폴더 수',3],['문서 기준 상품명 수',2],['원본 PDF / ZIP 수','7 / 3'],['중복 제외 PDF 수',5],['주 약관 페이지 합계',301]];s.getRange('A9:B14').format.rowHeight=26;
const notes=[
'분석 단위: 보험금 지급기준표의 담보 하나를 한 행으로 기록. 백년친구의 1종·2종은 담보명에 종형을 표시하여 구분.',
'중복 처리: e-생활보험과 생활보험 폴더의 약관·사업방법서는 SHA-256이 동일. 문서 상품명인 무배당 백년친구 생활보험(2507)으로 한 번만 기록. e 상품의 별도 자료 여부는 추가 확인 필요.',
'보장금액: 원문 지급표의 보험가입금액 1,000만원 기준 금액을 명시. 실제 계약 보험가입금액에 따라 달라질 수 있으며 감액기간·횟수 한도를 함께 기록.',
'분석 범위: 주 약관의 지급기준표 3개와 관련 보장 조항 및 사업방법서 대조. ZIP 내부 PDF는 기존 PDF와 동일하며 약관_2.pdf는 법·규정 부록으로 담보 생성에서 제외.',
'계약 소멸 시 사망 적립액 반환은 별도 담보 행으로 생성하지 않음. 지급기준표 주석은 출처·검토 시트에 원문 내용으로 보존.',
'출처: PDF 페이지는 실제 파일 페이지 번호. 출처·검토 시트의 id로 담보데이터와 연결. 보장조건은 지급 조건과 관련 제외사항을 발췌하며 세부 분류표·전체 약관도 함께 확인.',
'긴 조건은 셀 선택 후 수식 입력줄에서 전체 확인 가능. 원문 추출에 따른 띄어쓰기·페이지 번호가 일부 포함될 수 있음.',
'생성·수정일시는 +09:00 시간대를 포함한 텍스트. 통합 시 id를 전체 데이터 기준으로 다시 부여해야 함.'
];s.getRange('A17:A24').values=notes.map(t=>[t]);notes.forEach((t,i)=>s.getRange(`A${17+i}:C${17+i}`).format.rowHeight=Math.ceil(t.length/58)*17+14);
const ph=['id','상품명','종형','약관 파일','지급표 PDF 페이지','본문 PDF 페이지','동일 자료 출처','검토사항','지급기준표 주석'];
p.getRange('A1:I20').values=[ph,...r.map(x=>[x.id,x.product_name,x.type,x.source_file,x.source_page,x.article_pages,x.duplicate_paths.join('\n'),x.review,x.table_notes])];style(p,20,[8,45,25,100,20,20,100,65,120]);head(p,'A1:I1');p.getRange('A2:I20').format.rowHeight=145;p.tables.add('A1:I20',true,'DBSources');p.freezePanes.freezeRows(1);
w.recalculate();console.log((await w.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!',options:{useRegex:true,maxResults:10},maxChars:500})).ndjson);
for(const [sheetName,range,name] of [['담보데이터','A1:D3','data'],['담보데이터','E1:G2','details'],['처리현황','A2:C24','summary'],['출처·검토','A1:C3','sources']]){const b=await w.render({sheetName,range,scale:1.5,format:'png'});await fs.writeFile(`${root}/${name}_preview.png`,new Uint8Array(await b.arrayBuffer()));}
await (await SpreadsheetFile.exportXlsx(w)).save('outputs/DB생명_2507_담보분석.xlsx');console.log('saved 19 rows');
