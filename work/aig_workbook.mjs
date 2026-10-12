import fs from 'node:fs/promises';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const root='work/aig';
const records=JSON.parse(await fs.readFile(`${root}/records.json`,'utf8'));
const files=JSON.parse(await fs.readFile(`${root}/manifest.json`,'utf8'));
const w=Workbook.create();
const data=w.worksheets.add('담보데이터'),summary=w.worksheets.add('처리현황'),source=w.worksheets.add('출처·검토');
const headers=['id','company_name','product_name','coverage_name','coverage_target','coverage_amount','coverage_conditions','created_at','updated_at'];
const rows=records.map(r=>[r.id,'AIG손해보험',r.product,r.name,r.target,r.amount,r.conditions,r.created_at,r.updated_at]);
function style(s,rowCount,widths){s.showGridLines=false;const all=s.getRangeByIndexes(0,0,rowCount,widths.length);all.format.font={name:'Malgun Gothic',size:10};all.format.wrapText=true;all.format.verticalAlignment='top';for(let c=0;c<widths.length;c++)s.getRangeByIndexes(0,c,rowCount,1).format.columnWidth=widths[c];}
function head(s,range){s.getRange(range).format={fill:'#153957',font:{name:'Malgun Gothic',size:10,bold:true,color:'#FFFFFF'},rowHeight:30,wrapText:true};}
data.getRange(`A1:I${rows.length+1}`).values=[headers,...rows];style(data,rows.length+1,[8,16,46,65,65,90,150,30,30]);head(data,'A1:I1');data.tables.add(`A1:I${rows.length+1}`,true,'AIGCoverageData');data.freezePanes.freezeRows(1);data.freezePanes.freezeColumns(2);data.tabColor='#153957';data.getRange(`A2:A${rows.length+1}`).setNumberFormat('0');data.getRange(`H2:I${rows.length+1}`).setNumberFormat('@');
for(let i=0;i<rows.length;i++){
 let lines=4;for(const [c,cap] of [[2,30],[3,44],[4,44],[5,62],[6,105]])lines=Math.max(lines,String(rows[i][c]).split('\n').reduce((n,t)=>n+Math.ceil(t.length/cap)+1,0));data.getRange(`A${i+2}:I${i+2}`).format.rowHeight=Math.min(409,Math.max(90,lines*14+10));
}
style(summary,28,[70,17,19,23,22]);summary.getRange('A2').values=[['AIG손해보험 상품공시 담보 분석']];summary.getRange('A2').format.font={name:'Malgun Gothic',size:14,bold:true,color:'#153957'};
summary.getRange('A4:E7').values=[['상품명','담보 행 수','약관 페이지','상품요약서 페이지','사업방법서 페이지'],...[0,1,2].map(d=>[records.find(r=>r.doc===d).product,records.filter(r=>r.doc===d).length,files[d*3+2].pages,files[d*3+1].pages,files[d*3].pages])];head(summary,'A4:E4');summary.getRange('A5:E7').format.rowHeight=42;
summary.getRange('A9:B13').values=[['전체 담보 행 수',records.length],['상품 수',3],['원본 PDF 수',files.length],['중복 제외 PDF 수',new Set(files.map(f=>f.hash)).size],['전체 약관 페이지',435]];summary.getRange('A9:B13').format.rowHeight=27;summary.getRange('B5:E7').setNumberFormat('0');summary.getRange('B9:B13').setNumberFormat('0');
const notes=[
 '분석 기준 — 상품별 담보 하나를 한 행으로 저장. 전이암진단비의 림프절전이암·특정전이암 세부보장은 별도 행으로 구분.',
 '문서 대조 — 사업방법서로 상품명·가입 범위 확인. 상품요약서의 담보 목록·지급표를 약관의 보장 조항 및 공통 제외사항과 연결.',
 '보장금액 — 고정 가입금액을 추정하지 않고 보험가입금액·지급비율·감액기간·산식으로 기록. 가입금액은 개별 보험증권 기준.',
 '심사유형 — 305간편심사형, 325간편심사형, 일반 암보험을 별도 상품으로 유지. 원문에 기재된 간편심사 담보명도 보존.',
 '검증 범위 — 9개 파일의 중복 확인, 전체 약관 435페이지 추출, 담보별 약관 제목 연결, 필수값·중복·지급표 연결 검사 및 대표 원문 시각 대조.',
 '긴 조건 읽기 — 셀을 선택하면 수식 입력줄에서 전체 내용을 확인할 수 있음. 원문 줄바꿈에 따른 일부 띄어쓰기 차이가 있으며, 긴 셀은 화면에서 일부만 보일 수 있음.',
 '생성·수정일시 — 시간대를 포함한 날짜·시각 문자열(+09:00)로 저장. Excel에는 TIMESTAMPTZ 형식이 없어 텍스트로 기록.',
 '출처 확인 — 출처·검토의 id로 담보데이터 행과 연결. 페이지는 PDF의 실제 페이지 번호이며 상품요약서와 약관을 함께 기재.'
];summary.getRange('A16:A23').values=notes.map(t=>[t]);for(let i=0;i<notes.length;i++)summary.getRange(`A${16+i}:E${16+i}`).format.rowHeight=Math.ceil(notes[i].length/46)*15+12;
const sh=['id','상품명','담보명','상품요약서 파일','요약서 PDF 페이지','약관 파일','약관 PDF 페이지','검토사항'];
const sr=records.map(r=>[r.id,r.product,r.name,r.summary_path,r.end_page?`${r.page}–${r.end_page}`:String(r.page),r.policy_path,`${r.policy_start}–${r.policy_end}`,r.review]);
source.getRange(`A1:H${sr.length+1}`).values=[sh,...sr];style(source,sr.length+1,[8,46,65,105,20,105,20,55]);head(source,'A1:H1');source.getRange(`A2:H${sr.length+1}`).format.rowHeight=100;source.tables.add(`A1:H${sr.length+1}`,true,'AIGSources');source.freezePanes.freezeRows(1);
w.recalculate();console.log((await w.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:20},maxChars:1000})).ndjson);
console.log((await w.inspect({kind:'table',range:'담보데이터!A1:F3',tableMaxRows:3,tableMaxCols:6,tableMaxCellChars:90,maxChars:1600})).ndjson);
for(const [s,range,name] of [['담보데이터','A1:D3','data'],['담보데이터','E1:G2','details'],['처리현황','A2:E23','summary'],['출처·검토','A1:C3','sources']]){const blob=await w.render({sheetName:s,range,scale:1.5,format:'png'});await fs.writeFile(`${root}/${name}_preview.png`,new Uint8Array(await blob.arrayBuffer()));}
const x=await SpreadsheetFile.exportXlsx(w);await x.save('outputs/AIG손해보험_2507_담보분석.xlsx');console.log('saved',rows.length);
