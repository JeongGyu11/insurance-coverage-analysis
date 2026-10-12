import fs from 'node:fs/promises';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const root='work/lotte',r=JSON.parse(await fs.readFile(`${root}/records.json`,'utf8')),m=JSON.parse(await fs.readFile(`${root}/manifest.json`,'utf8'));
const w=Workbook.create(),d=w.worksheets.add('담보데이터'),s=w.worksheets.add('처리현황'),p=w.worksheets.add('출처·검토'),last=r.length+1;
const h=['id','company_name','product_name','coverage_name','coverage_target','coverage_amount','coverage_conditions','created_at','updated_at'];
function style(sheet,n,widths){sheet.showGridLines=false;const a=sheet.getRangeByIndexes(0,0,n,widths.length);a.format.font={name:'Malgun Gothic',size:10};a.format.wrapText=true;a.format.verticalAlignment='top';widths.forEach((v,c)=>sheet.getRangeByIndexes(0,c,n,1).format.columnWidth=v);}
function head(sheet,range){sheet.getRange(range).format={fill:'#153957',font:{name:'Malgun Gothic',size:10,bold:true,color:'#FFFFFF'},rowHeight:32,wrapText:true};}
d.getRange(`A1:I${last}`).values=[h,...r.map(x=>h.map(k=>x[k]))];style(d,last,[8,22,46,65,80,110,150,30,30]);head(d,'A1:I1');d.tables.add(`A1:I${last}`,true,'LotteCoverageData');d.freezePanes.freezeRows(1);d.freezePanes.freezeColumns(2);d.getRange(`H2:I${last}`).setNumberFormat('@');d.getRange(`A2:I${last}`).format.rowHeight=140;
r.forEach((x,i)=>{if(x.review.startsWith('확인 필요'))d.getRange(`A${i+2}:I${i+2}`).format.fill='#FFF1CC';});
style(s,29,[110,25,38]);s.getRange('A2').values=[['롯데손해보험 · 2025년 7월 상품공시 담보 분석']];s.getRange('A2').format.font={name:'Malgun Gothic',size:15,bold:true,color:'#153957'};
const products=[...new Set(r.map(x=>x.product_name))];s.getRange('A4:C6').values=[['상품명','담보·확장특약 행 수','분석 자료'],...products.map(n=>[n,r.filter(x=>x.product_name===n).length,'사업방법서·상품요약서·약관'])];head(s,'A4:C4');s.getRange('A5:C6').format.rowHeight=40;
s.getRange('A8:B13').values=[['전체 담보·확장특약 행 수',r.length],['상품 폴더 / 원본 PDF 수','2 / 6'],['약관 페이지 합계',m.filter(x=>x.kind==='약관').reduce((a,x)=>a+x.pages,0)],['전용 약관 확인 필요',r.filter(x=>x.review.startsWith('확인 필요')).length],['형별 분류','사이버보험 21행 / 국내여행보험 58행'],['분석 범위','폴더 내 2025년 7월 자료 전체']];s.getRange('A8:B13').format.rowHeight=30;
const notes=[
'분석 단위: 상품별 담보 한 행. 사망·후유장해, 개인정보·신용도용의 금전손해·법률비용, 사이버폭력·스토킹의 법률비용·심리상담비용은 구분. 실손의료비는 급여·비급여 및 세부 치료별 7행으로 구분.',
'선택 및 확장: 안심사이버보험은 별도 기본담보 없이 선택특약을 부가. 국내여행보험은 기본 상해사망·후유장해와 선택특약 구분. 부재·운동위험 특약 3행은 기존 담보의 면책범위 확장으로 별도 추가 보험금으로 합산하지 않음.',
'금액 기준: 상품요약서 보험료 예시의 가입금액·자기부담금을 실제 계약조건으로 확정하지 않음. 계약별 보험가입금액·총한도·사고별 한도·공제비율·정액 지급기준을 기록. 장해·부상 급수는 약관 비율 적용.',
'한도 공유: 안심사이버보험의 총보상한도 설정 여부 및 담보별 자기부담금은 보험증권 기준. 사이버폭력·스토킹 심리상담비의 40% 한도와 한도 공유 시 산식을 기록. 개별 상해특약의 지급기준은 해당 조항을 우선 확인.',
'확인 필요 1행: 자동차사고부상(비운전자)(1~10급)은 요약서 PDF 3페이지에 있으나 제공 약관에는 운전자 담보만 존재. 비운전자 지급비율·면책은 확인 불가로 표시하며 운전자 내용을 임의 적용하지 않음. 해당 데이터 행은 노란색 표시.',
'원문 차이: 요약서의 입원일당 일반 안내 180일과 달리 식중독입원일당은 4일째부터 1회 입원당 120일 한도. 약관을 우선 반영. 국민건강보험 미가입자 추가특약은 기본형 실손의료비 행의 적용조건에 함께 기재.',
'범위 및 출처: 단체·가족계약, 보험료정산·전자서명·환율·청구대행 등 독립 지급담보 없는 운영특약은 별도 담보 행에서 제외. 출처·검토의 id로 원문 파일 및 실제 PDF 페이지를 연결. 요약서 페이지는 담보·금액·제한 안내 대조 범위.',
'검증 및 열람: 지급조항·요약서 담보목록 연결, 주요 지급표 시각 대조, 필수값·중복·저장값 검증. 긴 조건은 셀 선택 후 수식 입력줄에서 전체 내용 확인. 생성·수정일시는 +09:00 텍스트.'
];s.getRange('A16:A23').values=notes.map(x=>[x]);notes.forEach((t,i)=>s.getRange(`A${16+i}:C${16+i}`).format.rowHeight=Math.ceil(t.length/73)*17+14);
const ph=['id','상품명','담보명','상품요약서 파일','요약서 PDF 페이지','약관 파일','관련 약관 PDF 페이지','약관 담보·특약명','사업방법서 파일','검토사항'];p.getRange(`A1:J${last}`).values=[ph,...r.map(x=>[x.id,x.product_name,x.coverage_name,x.summary_file,x.summary_page,x.source_file||'전용 약관 미제공(상품요약서 기준)',x.source_page,x.source_name,x.business_file,x.review])];style(p,last,[8,46,65,110,25,110,30,80,110,115]);head(p,'A1:J1');p.getRange(`A2:J${last}`).format.rowHeight=110;p.tables.add(`A1:J${last}`,true,'LotteSources');p.freezePanes.freezeRows(1);
r.forEach((x,i)=>{if(x.review.startsWith('확인 필요'))p.getRange(`A${i+2}:J${i+2}`).format.fill='#FFF1CC';});
w.recalculate();console.log((await w.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!',options:{useRegex:true,maxResults:10},maxChars:500})).ndjson);
for(const [sheetName,range,name] of [['담보데이터','A1:D3','data'],['담보데이터','E1:G2','details'],['처리현황','A2:C23','summary'],['출처·검토','A1:C3','sources']]){const b=await w.render({sheetName,range,scale:1.3,format:'png'});await fs.writeFile(`${root}/${name}_preview.png`,new Uint8Array(await b.arrayBuffer()));}
await fs.mkdir('outputs',{recursive:true});await (await SpreadsheetFile.exportXlsx(w)).save('outputs/롯데손해보험_2507_담보분석.xlsx');console.log('saved',r.length);
