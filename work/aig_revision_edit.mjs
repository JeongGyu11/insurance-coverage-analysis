import fs from 'node:fs/promises';
import {SpreadsheetFile,FileBlob} from '@oai/artifact-tool';
const r=JSON.parse(await fs.readFile('work/aig/revision/revised.json','utf8'));
const w=await SpreadsheetFile.importXlsx(await FileBlob.load('work/aig/revision/original.xlsx'));
const data=w.worksheets.getItem('담보데이터'),summary=w.worksheets.getItem('처리현황');
data.getRange('E2:G123').values=r.map(x=>[x.target,x.amount,x.conditions]);
data.getRange('I2:I123').values=r.map(x=>[x.updated_at]);
for(const [col,width] of [['E',75],['F',95],['G',110]])data.getRange(`${col}1:${col}123`).format.columnWidth=width;
for(let i=0;i<r.length;i++){
 const x=r[i],lines=Math.max(4,Math.ceil(x.target.length/44),Math.ceil(x.amount.length/57),Math.ceil(x.conditions.length/65));
 data.getRange(`A${i+2}:I${i+2}`).format.rowHeight=Math.min(409,lines*17+15);
}
const notes={
 A18:'보장금액 — 보험증권상 가입금액과 지급비율·단위·감액기간을 설명. 입원일당·통원 회당·실제 간병서비스 사용일을 구분. 계약별 가입금액을 고정 금액으로 추정하지 않음.',
 A20:'수정 검증 — 3상품 122행 및 기존 id·보험사·상품·담보·생성일시·출처 유지. 지급금액의 기존 비율과 약관상 면책·감액·횟수·일수 제한을 대조.',
 A21:'보장대상·조건 — 보장대상은 질병·진단·수술·치료·의료기관 범위를 설명. 보장조건은 면책·감액, 지급 한도, 중복·차감, 주요 제외사항 위주로 정리. 분쟁·청구 절차는 생략.'
};
for(const [cell,value] of Object.entries(notes)){summary.getRange(cell).values=[[value]];summary.getRange(`${cell}:E${cell.slice(1)}`).format.rowHeight=Math.ceil(value.length/46)*17+15;}
w.recalculate();
console.log((await w.inspect({kind:'table',range:'담보데이터!E2:G2',tableMaxRows:1,tableMaxCols:3,tableMaxCellChars:160,maxChars:1600})).ndjson);
console.log((await w.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:20},maxChars:1000})).ndjson);
for(const [sheetName,range,name] of [['담보데이터','E2:G4','diagnosis'],['담보데이터','E28:G29','hospital'],['담보데이터','E35:G37','care'],['처리현황','A16:E23','criteria']]){
 const blob=await w.render({sheetName,range,scale:1,format:'png'});
 await fs.writeFile(`work/aig/revision/${name}.png`,new Uint8Array(await blob.arrayBuffer()));
}
const out=await SpreadsheetFile.exportXlsx(w);
await out.save('outputs/01a10ed0-eb0e-7720-80fe-23aace7c950b/AIG손해보험_2507_담보분석.xlsx');
console.log('SAVED 122 rows');
