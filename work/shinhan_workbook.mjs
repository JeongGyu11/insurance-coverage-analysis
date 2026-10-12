import fs from 'node:fs/promises';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const root='work/shinhan',r=JSON.parse(await fs.readFile(`${root}/records.json`,'utf8')),m=JSON.parse(await fs.readFile(`${root}/manifest.json`,'utf8'));
const w=Workbook.create(),d=w.worksheets.add('담보데이터'),s=w.worksheets.add('처리현황'),p=w.worksheets.add('출처·검토'),last=r.length+1;
const h=['id','company_name','product_name','coverage_name','coverage_target','coverage_amount','coverage_conditions','created_at','updated_at'];
function style(sheet,n,widths){sheet.showGridLines=false;const a=sheet.getRangeByIndexes(0,0,n,widths.length);a.format.font={name:'Malgun Gothic',size:10};a.format.wrapText=true;a.format.verticalAlignment='top';widths.forEach((v,c)=>sheet.getRangeByIndexes(0,c,n,1).format.columnWidth=v);}
function head(sheet,range){sheet.getRange(range).format={fill:'#153957',font:{name:'Malgun Gothic',size:10,bold:true,color:'#FFFFFF'},rowHeight:32,wrapText:true};}
d.getRange(`A1:I${last}`).values=[h,...r.map(x=>h.map(k=>x[k]))];style(d,last,[8,20,55,70,78,112,145,30,30]);head(d,'A1:I1');d.tables.add(`A1:I${last}`,true,'ShinhanCoverageData');d.freezePanes.freezeRows(1);d.freezePanes.freezeColumns(2);d.getRange(`H2:I${last}`).setNumberFormat('@');
r.forEach((x,i)=>{const lines=Math.max(6,Math.ceil(x.coverage_name.length/44),Math.ceil(x.coverage_target.length/46),Math.ceil(x.coverage_amount.length/68),Math.ceil(x.coverage_conditions.length/87));d.getRange(`A${i+2}:I${i+2}`).format.rowHeight=Math.min(409,Math.max(110,lines*17+18));});
style(s,36,[108,17,28,90]);s.getRange('A2').values=[['신한라이프 · 2025년 7월 상품공시 담보 분석']];s.getRange('A2').format.font={name:'Malgun Gothic',size:15,bold:true,color:'#153957'};
const products=[...new Set(r.map(x=>x.product_name))];s.getRange('A4:D8').values=[['상품·자료','담보 행 수','처리','설명'],...products.map(n=>[n,r.filter(x=>x.product_name===n).length,'분석 완료',n.includes('ONE')?'가입 당시 만15세 기준·연금형태별 사망 지급금 및 금리연동연금 산식 구분.':'판매채널에 따른 상품명 구분을 유지. 거치형·생활자금형, 연금형태별 지급구조 분석.']),['보험수익자신탁변경특약',0,'운영특약 검토','보험수익자를 신탁회사로 변경하고 기존 보험금을 수령·관리하는 제도. 독립 지급담보를 만들지 않음.']];head(s,'A4:D4');s.getRange('A5:D8').format.rowHeight=70;
s.getRange('A10:B12').values=[['전체 담보 행 수',r.length],['원본 폴더 / PDF 수','4 / 8'],['원본 약관 페이지 합계',m.filter(x=>x.kind==='약관').reduce((a,x)=>a+x.pages,0)]];s.getRange('A10:B12').format.rowHeight=28;
s.getRange('A14:D22').values=[['원본 자료','구분','PDF 페이지','원본 파일'],...m.map(x=>[x.product.replace(/^(판매완료|판매중)__20250701_/,''),x.kind,x.pages,x.path])];head(s,'A14:D14');s.getRange('A15:D22').format.rowHeight=65;
const notes=[
'분석 기준: 폴더의 2025년 7월 공시 자료 전체 8개 PDF를 검토. 담보데이터는 요청한 9개 컬럼과 순서를 유지하고 지급구조별 한 행으로 작성. 상품의 선택 가능한 기간·성별·나이에 따른 지급률은 해당 행에서 명시하며 선택값마다 중복 행을 만들지 않음.',
'명칭 대조: 사업방법서 PDF 3에는 금융기관 보험대리점 채널의 상품명을 SOL메이트달러연금보험(무배당)으로 표시한다고 명시. 두 달러연금의 사업방법서는 파일 해시가 같고 약관 지급내용도 상품명·문서코드 외 동일. 폴더별 추적을 위해 두 상품명을 유지했으므로 통합 DB에서 판매채널명을 하나로 정규화할 경우 동일 지급내용의 중복을 검토해야 함.',
'대상·금액·조건: DB 예시와 같은 설명문으로 피보험자·생존·장해·가입나이 범위를 설명. 정액(US$10,000/1,000만원), 생활자금과 연금 산식, 사망 지급금의 최저보증·감액·인출을 구분. 조건은 지급기간·횟수·형태 변경·주요 제한 위주로 작성하며 청구서류·분쟁 절차는 반복하지 않음.',
'ONE더라이프: 최저연금기준금액의 7%/5% 또는 6%/4%는 납입보험료별로 일자 계산하여 가산하는 기준금액 비율이며 계약자적립액의 복리 공시이율 또는 실제 연금 지급률이 아님. 실제 연금 지급률은 개시나이·성별의 기본지급률 × (1+장기유지가산율). 100세 최종 지급일은 약관상 피보험자 99세 계약해당일.',
'달러연금: 고도재해장해 US$10,000은 정액 지급이며 생활자금은 가입시 확정 월액. 계약체결 시 종신연금형을 선택하고 개시일 전일까지 확정·상속연금형으로 변경 가능. 원화 환산을 임의로 적용하지 않고 금액 통화를 US$로 기록.',
'담보 제외 내역: 보험금 대리청구 지정서비스(달러약관 PDF 77–82/ONE PDF 87–92)는 청구제도. ONE의 다자녀가정우대특약(PDF 81–86)은 보험료 할인제도. 보험수익자신탁변경특약 약관 PDF 3–6은 주계약 보험금 수령자를 신탁회사로 변경하는 제도. 각각 별도 보험금 지급액을 추가하지 않고 검토 완료로 처리.',
'검토·출처: 원문 텍스트와 지급기준표·지급률·가입조건의 PDF 이미지 대조. 출처·검토 시트의 id로 해당 약관·사업방법서와 실제 PDF 페이지를 찾을 수 있음. 생성·수정일시는 +09:00을 포함한 텍스트로 저장. 자료에 실린 공시이율 최저보증은 해당 계약 약관의 기준이며 현재 판매상품의 이율을 뜻하지 않음.'
];s.getRange('A25:A31').values=notes.map(x=>[x]);notes.forEach((t,i)=>s.getRange(`A${25+i}:D${25+i}`).format.rowHeight=Math.ceil(t.length/64)*17+14);
const ph=['id','상품명','담보명','약관 파일','약관 PDF 페이지','사업방법서 파일','사업방법서 PDF 페이지','검토내용'];p.getRange(`A1:H${last}`).values=[ph,...r.map(x=>[x.id,x.product_name,x.coverage_name,x.source_file,x.source_page,x.business_file,x.business_page,x.review])];style(p,last,[8,55,70,110,28,110,28,110]);head(p,'A1:H1');p.getRange(`A2:H${last}`).format.rowHeight=110;p.tables.add(`A1:H${last}`,true,'ShinhanCoverageSources');p.freezePanes.freezeRows(1);
w.recalculate();
console.log((await w.inspect({kind:'table',range:'처리현황!A4:D8',include:'values',tableMaxRows:5,tableMaxCols:4,maxChars:1800})).ndjson);
console.log((await w.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:10},maxChars:500})).ndjson);
for(const [sheetName,range,name] of [['담보데이터','A1:D4','data'],['담보데이터','E2:G3','dollar'],['담보데이터','E25:G26','one'],['처리현황','A2:D12','summary'],['처리현황','A25:A31','notes'],['출처·검토','A1:C4','sources']]){const b=await w.render({sheetName,range,scale:1.2,format:'png'});await fs.writeFile(`${root}/${name}_preview.png`,new Uint8Array(await b.arrayBuffer()));}
await (await SpreadsheetFile.exportXlsx(w)).save('outputs/01a10ed0-eb0e-7720-80fe-23aace7c950b/신한라이프_2507_담보분석.xlsx');console.log('SAVED',r.length);
