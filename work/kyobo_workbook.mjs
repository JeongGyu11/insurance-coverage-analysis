import fs from 'node:fs/promises';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const root='work/kyobo',r=JSON.parse(await fs.readFile(`${root}/records.json`,'utf8')),m=JSON.parse(await fs.readFile(`${root}/manifest.json`,'utf8'));
const w=Workbook.create(),d=w.worksheets.add('담보데이터'),s=w.worksheets.add('처리현황'),p=w.worksheets.add('출처·검토'),last=r.length+1;
const h=['id','company_name','product_name','coverage_name','coverage_target','coverage_amount','coverage_conditions','created_at','updated_at'];
function style(sheet,n,widths){sheet.showGridLines=false;const a=sheet.getRangeByIndexes(0,0,n,widths.length);a.format.font={name:'Malgun Gothic',size:10};a.format.wrapText=true;a.format.verticalAlignment='top';widths.forEach((v,c)=>sheet.getRangeByIndexes(0,c,n,1).format.columnWidth=v);}
function head(sheet,range){sheet.getRange(range).format={fill:'#153957',font:{name:'Malgun Gothic',size:10,bold:true,color:'#FFFFFF'},rowHeight:32,wrapText:true};}
d.getRange(`A1:I${last}`).values=[h,...r.map(x=>h.map(k=>x[k]))];style(d,last,[8,18,53,85,65,100,150,30,30]);head(d,'A1:I1');d.tables.add(`A1:I${last}`,true,'KyoboCoverageData');d.freezePanes.freezeRows(1);d.freezePanes.freezeColumns(2);d.getRange(`H2:I${last}`).setNumberFormat('@');d.getRange(`A2:I${last}`).format.rowHeight=140;
style(s,29,[100,22,35]);s.getRange('A2').values=[['교보생명 · 2025년 7월 상품공시 담보 분석']];s.getRange('A2').format.font={name:'Malgun Gothic',size:15,bold:true,color:'#153957'};
const products=[...new Set(r.map(x=>x.product_name))];s.getRange('A4:C10').values=[['상품 / 특약 폴더','담보 행 수','분석 자료'],...products.map(n=>[n,r.filter(x=>x.product_name===n).length,'사업방법서·약관'])];head(s,'A4:C4');s.getRange('A5:C10').format.rowHeight=40;
s.getRange('A12:B16').values=[['전체 담보 행 수',r.length],['상품·특약 폴더 수',products.length],['원본 PDF 수',m.length],['약관 페이지 합계',m.filter(x=>x.kind==='약관').reduce((a,x)=>a+x.pages,0)],['분석 범위','폴더 내 2025년 7월 자료 전체']];s.getRange('A12:B16').format.rowHeight=30;
const notes=[
'분석 단위: 상품별 주계약·선택특약·전환 후 계약의 담보를 한 행씩 기록. 담보명에 특약명을 함께 표시해 같은 지급명칭이 서로 섞이지 않도록 구분.',
'선택·전환 조건: 약관에 포함된 선택특약은 실제 부가 시에만 적용. 일반종신·적립형 전환계약, 연금전환특약, 장기요양전환특약 등은 해당 전환 신청·승낙 및 지급조건 충족 시 적용. 제공 자료 기준으로 정리.',
'금액 기준: 약관의 가입금액 1,000만원 기준 지급표는 기준을 표시. 실제 가입금액·계약자적립액에 따라 달라지는 금액은 산식·비율로 기록. 사망보험금 체증 방식과 감액기간은 해당 조항을 함께 기록.',
'형별 지급: 최초계약·갱신계약 및 특약의 형별 지급표 차이는 같은 담보 행의 보장금액·조건에 함께 기록. 1~5형 특정3대질환 납입면제는 형별 행으로 구분하며 공통 약관의 다른 형 조항은 해당 행에 적용하지 않음.',
'납입면제와 지급 제도: 보험료 납입면제는 현금 보험금이 아닌 면제 보장으로 표시. 장기간병·사망 선지급, 사후정리·양육연금은 기존 사망보험금의 선지급·분할지급 제도로 별도의 추가 사망보험금이 아님.',
'분석에서 제외: 건강체할인특약Ⅱ는 보험료 할인 제도, 지정대리청구서비스특약은 청구 대행 제도로 별도 보험금 지급 담보가 없어 담보 행에서 제외.',
'출처: 상품요약서 파일은 제공되지 않았으므로 약관 지급표와 지급·정의·보장개시 조항 기준으로 분석. 출처·검토의 id로 연결하며 PDF 페이지는 실제 페이지 번호(인쇄된 약관 쪽수와 다름).',
'검증 및 열람: 지급표의 합쳐진 셀·다음 페이지 연결 보정, 주요 원문 시각 대조, 필수값·중복·저장값 검사. 긴 조건은 셀 선택 후 수식 입력줄에서 전체 내용 확인. 생성·수정일시는 +09:00 텍스트.'
];s.getRange('A19:A26').values=notes.map(x=>[x]);notes.forEach((t,i)=>s.getRange(`A${19+i}:C${19+i}`).format.rowHeight=Math.ceil(t.length/67)*17+14);
const ph=['id','상품명','담보명','약관 파일','지급표·조항 PDF 페이지','관련 특약 PDF 범위','약관 주계약·특약명','검토사항'];p.getRange(`A1:H${last}`).values=[ph,...r.map(x=>[x.id,x.product_name,x.coverage_name,x.source_file,x.source_page,x.article_pages,x.source_name,x.review])];style(p,last,[8,53,85,115,27,25,90,110]);head(p,'A1:H1');p.getRange(`A2:H${last}`).format.rowHeight=110;p.tables.add(`A1:H${last}`,true,'KyoboSources');p.freezePanes.freezeRows(1);
w.recalculate();console.log((await w.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!',options:{useRegex:true,maxResults:10},maxChars:500})).ndjson);
for(const [sheetName,range,name] of [['담보데이터','A1:D3','data'],['담보데이터','E1:G2','details'],['처리현황','A2:C26','summary'],['출처·검토','A1:C3','sources']]){const b=await w.render({sheetName,range,scale:1.3,format:'png'});await fs.writeFile(`${root}/${name}_preview.png`,new Uint8Array(await b.arrayBuffer()));}
await fs.mkdir('outputs',{recursive:true});await (await SpreadsheetFile.exportXlsx(w)).save('outputs/교보생명_2507_담보분석.xlsx');console.log('saved',r.length);
