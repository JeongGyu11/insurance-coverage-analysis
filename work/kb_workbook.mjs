import fs from 'node:fs/promises';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const root='work/kb',r=JSON.parse(await fs.readFile(`${root}/records.json`,'utf8')),m=JSON.parse(await fs.readFile(`${root}/manifest.json`,'utf8'));
const w=Workbook.create(),d=w.worksheets.add('담보데이터'),s=w.worksheets.add('처리현황'),p=w.worksheets.add('출처·검토');
const h=['id','company_name','product_name','coverage_name','coverage_target','coverage_amount','coverage_conditions','created_at','updated_at'],last=r.length+1;
function style(sheet,n,widths){sheet.showGridLines=false;const a=sheet.getRangeByIndexes(0,0,n,widths.length);a.format.font={name:'Malgun Gothic',size:10};a.format.wrapText=true;a.format.verticalAlignment='top';widths.forEach((v,c)=>sheet.getRangeByIndexes(0,c,n,1).format.columnWidth=v);}
function head(sheet,range){sheet.getRange(range).format={fill:'#153957',font:{name:'Malgun Gothic',size:10,bold:true,color:'#FFFFFF'},rowHeight:32,wrapText:true};}
d.getRange(`A1:I${last}`).values=[h,...r.map(x=>h.map(k=>x[k]))];style(d,last,[8,20,66,42,52,80,130,30,30]);head(d,'A1:I1');d.tables.add(`A1:I${last}`,true,'KBCoverageData');d.freezePanes.freezeRows(1);d.freezePanes.freezeColumns(2);d.getRange(`H2:I${last}`).setNumberFormat('@');
r.forEach((x,i)=>d.getRange(`A${i+2}:I${i+2}`).format.rowHeight=Math.min(409,Math.max(95,x.coverage_conditions.split('\n').reduce((n,t)=>n+Math.ceil(t.length/90)+1,0)*14)));
style(s,28,[105,22,30]);s.getRange('A2').values=[['KB라이프생명 상품공시 담보 분석']];s.getRange('A2').format.font={name:'Malgun Gothic',size:15,bold:true,color:'#153957'};
const products=[...new Set(r.map(x=>x.product_name))];s.getRange('A4:C10').values=[['상품명','담보 / 급부 행 수','지급표 PDF 페이지'],...products.map(n=>[n,r.filter(x=>x.product_name===n).length,String(r.find(x=>x.product_name===n).source_page)])];head(s,'A4:C4');s.getRange('A5:C10').format.rowHeight=40;
s.getRange('A12:B16').values=[['전체 담보 / 급부 행 수',24],['상품 형태 수',6],['원본 PDF 수',14],['중복 제외 PDF 수',8],['중복 제외 약관 페이지 합계',837]];s.getRange('A12:B16').format.rowHeight=26;
const notes=[
'분석 기준: 골든라이프의 표준형·해약환급금 일부지급형과 상해·치매 보장형을 구분. 세번의 약속 연금보험은 보증형·미보증형을 사업방법서의 별도 보험종목에 따라 구분.',
'문서 대조: PDF 14개 중 동일 내용은 8개 파일로 중복 제거하여 추출. 골든라이프 약관 4개는 각각 검토. 연금 약관은 동일하지만 문서 안의 유형별 보증 조항을 구분 적용.',
'보장금액: 골든라이프 금액은 보험가입금액 1,000만원 기준이며 실제 계약에 따라 달라짐. 연금 고도재해장해급여금은 원문 월 40만원·36회. 생존연금은 고정금액 추정 없이 산식·계약별 기준 기록.',
'연금 급부: 고도재해장해급여금, 종신연금, 생활설계자금, 확정연금, 상속연금을 유형마다 5개 행으로 기록. 가입시 종신연금형이며 확정·상속 형태는 개시 전 변경 선택 기준.',
'별도 담보 행 제외: 제도성·보장제한 특약, 보험료 납입면제, 계약 소멸 시 사망 적립액 반환. 납입면제는 상해 보장조건에, 적립액 반환은 지급표 주석에 보존. 보증형의 최저적립액 보증은 연금 조건에 반영.',
'검토자료: 상품요약서는 골든라이프 표준형 상해·치매 폴더에 동일 파일로 제공. 일부지급형과 연금 폴더에는 상품요약서가 없어 사업방법서와 해당 약관으로 검토.',
'원문 추적: 출처·검토 시트의 id로 연결. 모든 페이지는 PDF 실제 페이지 번호. 긴 셀은 선택 후 수식 입력줄에서 전체 확인 가능. 조건은 발췌 내용이며 세부 분류표·전체 약관도 함께 확인.',
'생성·수정일시: +09:00 시간대를 포함한 텍스트. 통합할 때 id를 전체 데이터 기준으로 다시 부여. 원문 띄어쓰기와 표기 차이가 일부 남아 있음.'
];s.getRange('A19:A26').values=notes.map(t=>[t]);notes.forEach((t,i)=>s.getRange(`A${19+i}:C${19+i}`).format.rowHeight=Math.ceil(t.length/70)*17+14);
const ph=['id','상품명','담보 / 급부명','약관 파일','지급표 PDF 페이지','관련 본문 PDF 페이지','동일 자료 출처','검토사항','지급기준표 주석'];
p.getRange(`A1:I${last}`).values=[ph,...r.map(x=>[x.id,x.product_name,x.coverage_name,x.source_file,String(x.source_page),x.article_pages,x.duplicate_paths.filter(y=>y!==x.source_file).concat(m.find(y=>y.path===x.source_file)?[]:[m.find(y=>y.key==='doc7').path]).join('\n'),x.review,x.table_notes])];style(p,last,[8,66,42,110,20,30,110,80,130]);head(p,'A1:I1');p.getRange(`A2:I${last}`).format.rowHeight=180;p.tables.add(`A1:I${last}`,true,'KBSources');p.freezePanes.freezeRows(1);
w.recalculate();console.log((await w.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!',options:{useRegex:true,maxResults:10},maxChars:500})).ndjson);
console.log((await w.inspect({kind:'table',range:'담보데이터!A1:F3',tableMaxRows:3,tableMaxCols:6,tableMaxCellChars:60,maxChars:1200})).ndjson);
for(const [sheetName,range,name] of [['담보데이터','A1:D2','data'],['담보데이터','E1:G2','details'],['처리현황','A2:C26','summary'],['출처·검토','A1:C2','sources']]){const b=await w.render({sheetName,range,scale:1.5,format:'png'});await fs.writeFile(`${root}/${name}_preview.png`,new Uint8Array(await b.arrayBuffer()));}
await (await SpreadsheetFile.exportXlsx(w)).save('outputs/KB라이프생명_2507_담보분석.xlsx');console.log('saved 24 rows');
