import fs from 'node:fs/promises';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const root='work/mirae',r=JSON.parse(await fs.readFile(`${root}/records.json`,'utf8')),m=JSON.parse(await fs.readFile(`${root}/manifest.json`,'utf8'));
const w=Workbook.create(),d=w.worksheets.add('담보데이터'),s=w.worksheets.add('처리현황'),p=w.worksheets.add('출처·검토'),last=r.length+1;
const h=['id','company_name','product_name','coverage_name','coverage_target','coverage_amount','coverage_conditions','created_at','updated_at'];
function style(sheet,n,widths){sheet.showGridLines=false;const a=sheet.getRangeByIndexes(0,0,n,widths.length);a.format.font={name:'Malgun Gothic',size:10};a.format.wrapText=true;a.format.verticalAlignment='top';widths.forEach((v,c)=>sheet.getRangeByIndexes(0,c,n,1).format.columnWidth=v);}
function head(sheet,range){sheet.getRange(range).format={fill:'#153957',font:{name:'Malgun Gothic',size:10,bold:true,color:'#FFFFFF'},rowHeight:32,wrapText:true};}
d.getRange(`A1:I${last}`).values=[h,...r.map(x=>h.map(k=>x[k]))];style(d,last,[8,20,55,83,78,100,150,30,30]);head(d,'A1:I1');d.tables.add(`A1:I${last}`,true,'MiraeCoverageData');d.freezePanes.freezeRows(1);d.freezePanes.freezeColumns(2);d.getRange(`H2:I${last}`).setNumberFormat('@');
r.forEach((x,i)=>{const lines=Math.max(5,Math.ceil(x.coverage_name.length/52),Math.ceil(x.coverage_target.length/46),Math.ceil(x.coverage_amount.length/60),Math.ceil(x.coverage_conditions.length/92));d.getRange(`A${i+2}:I${i+2}`).format.rowHeight=Math.min(409,Math.max(90,lines*16+15));});
style(s,28,[118,25,38]);s.getRange('A2').values=[['미래에셋생명 · 2025년 7월 상품공시 담보 분석']];s.getRange('A2').format.font={name:'Malgun Gothic',size:15,bold:true,color:'#153957'};
const products=[...new Set(r.map(x=>x.product_name))];s.getRange('A4:C7').values=[['상품명','담보 행 수','분석 자료'],...products.map(n=>[n,r.filter(x=>x.product_name===n).length,'사업방법서·상품요약서·약관'])];head(s,'A4:C4');s.getRange('A5:C7').format.rowHeight=50;
s.getRange('A9:B13').values=[['전체 담보 행 수',r.length],['상품 폴더 / 원본 PDF 수','3 / 9'],['약관 페이지 합계',m.filter(x=>x.kind==='약관').reduce((a,x)=>a+x.pages,0)],['분석 범위','20250701 상품 폴더 내 자료 전체'],['일시 형식','생성·수정일시: +09:00을 포함한 텍스트']];s.getRange('A9:B13').format.rowHeight=32;
const notes=[
'분석 단위: 상품별 담보 한 행. 수술 종별, 관혈·비관혈, 재해·질병, 암군별 지급액, 일반·간편고지형, 연금형태별 지급과 실손의 입원·통원을 나누어 기록. 동일 지급구조의 기본형·해약환급금이 없는 유형은 해당 담보의 적용범위에 기재.',
'보장대상: 피보험자 및 질병·재해·장해·수술·입원·통원·생존의 범위를 설명. 보장금액: 실제 가입금액·지급비율·단위·체증 산식·공제 및 한도를 설명. 공시 보험료 예시 금액을 실제 계약의 고정 지급액으로 사용하지 않음.',
'보장조건: 담보별 지급 요건·대기기간·감액·횟수·기관 제한·주요 제외와 전환 요건 중심으로 설명. 약관의 분쟁·일반 정의·청구서류 등은 줄이고 지급 여부와 금액에 영향을 주는 사항을 남김. 보내주신 DB 예시의 설명문 형태 적용.',
'M-케어: 간병인 1일 사용금액 7만원 기준, 재해·질병 및 체증형 구분. 1-5종과 1-7종 급여수술의 가입금액·비율·횟수 구분. 암·뇌심 주요치료비는 최초 진단 후 최대 10년간 연간 1회 지급기간, 월지급 치료지원은 최초 36회 확정·최대 120회 구분.',
'경영인 정기보험: 일반가입형·간편고지형 사망보험금 구분. 10년 경과 후 가입금액 × 10% × (계약경과년수−9) 체증식을 기록. 신속지급·선지급은 기존 보험금 지급방식이며 추가 사망보험금이 아님. 전환 담보는 실제 전환 시 적용.',
'실손의료비: 상해·질병의 급여 및 비급여 입원·통원을 구분하고 3대비급여를 별도 기록. 종합형은 상해·질병 내용을 모두 보장하므로 별도 중복 행을 만들지 않음. 연간 한도는 해당 원인별 입원·통원 합산이며 별도 한도로 더하지 않음.',
'설명 보완: 수술종별 대표 대상·질병 및 검사 범위·병실 정원·가입금액 기준과 지급 단위를 구체화. 원문 대조로 요로결석 1년 대기, 질병수술 365일 후 재지급, 급여 수술 예외 등을 추가. 연금개시 전 사망시 지급금 1행을 추가해 총 230행. 기존 행의 생성일시는 유지하고 수정일시만 갱신.',
'담보에서 제외: 지정대리청구, 장애인전용보험 전환, 보험료 정산·중지·재개, 부담보·할증 등 독립 지급담보가 없는 운영제도. 지급에 영향을 주는 사항은 해당 담보 조건에 반영. 종신전환은 이 주계약에서 선택 가능한 일반·간편고지형만 기록.',
'자료 기준일: 폴더는 2025년 7월 공시 자료이며 약관 자체의 시행·개정일은 서로 다를 수 있음. 가입금액·보장기간·보험료·가입 제한은 개별 보험증권 및 선택특약 기준. 긴 셀은 수식 입력줄에서 전체 확인 가능.'
];s.getRange('A16:A24').values=notes.map(x=>[x]);notes.forEach((t,i)=>s.getRange(`A${16+i}:C${16+i}`).format.rowHeight=Math.ceil(t.length/75)*17+14);
const ph=['id','상품명','담보명','상품요약서 파일','요약서 PDF 페이지','약관 파일','관련 약관 PDF 범위','약관 주계약·특약명','사업방법서 파일','검토사항'];p.getRange(`A1:J${last}`).values=[ph,...r.map(x=>[x.id,x.product_name,x.coverage_name,x.summary_file,x.summary_page,x.source_file,x.source_page,x.source_name,x.business_file,x.review])];style(p,last,[8,55,83,110,25,110,28,85,110,110]);head(p,'A1:J1');p.getRange(`A2:J${last}`).format.rowHeight=110;p.tables.add(`A1:J${last}`,true,'MiraeSources');p.freezePanes.freezeRows(1);
w.recalculate();
console.log((await w.inspect({kind:'table',range:'처리현황!A4:C7',include:'values',tableMaxRows:4,tableMaxCols:3,maxChars:1800})).ndjson);
console.log((await w.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:10},maxChars:500})).ndjson);
for(const [sheetName,range,name] of [['담보데이터','A1:D3','data'],['담보데이터','E2:G3','details'],['담보데이터','E8:G8','surgery'],['담보데이터','E204:G204','annuity'],['담보데이터','E231:G231','added'],['처리현황','A2:C24','summary'],['출처·검토','A1:C3','sources']]){const b=await w.render({sheetName,range,scale:1.2,format:'png'});await fs.writeFile(`${root}/${name}_preview.png`,new Uint8Array(await b.arrayBuffer()));}
await (await SpreadsheetFile.exportXlsx(w)).save('outputs/01a10ed0-eb0e-7720-80fe-23aace7c950b/미래에셋생명_2507_담보분석.xlsx');console.log('SAVED',r.length);
