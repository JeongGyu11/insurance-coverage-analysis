import fs from 'node:fs/promises';
import {SpreadsheetFile,FileBlob} from '@oai/artifact-tool';
const r=JSON.parse(await fs.readFile('work/abl_revision/revised.json','utf8'));
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load('work/abl_revision/original.xlsx'));
const data=wb.worksheets.getItem('담보데이터');
const summary=wb.worksheets.getItem('처리현황');
const source=wb.worksheets.getItem('출처·검토');
data.getRange('E2:G651').values=r.map(x=>[x.target,x.amount_display,x.conditions_display]);
data.getRange('I2:I651').values=r.map(x=>[x.updated_at]);
data.getRange('E1:E651').format.columnWidth=75;
data.getRange('F1:F651').format.columnWidth=100;
data.getRange('G1:G651').format.columnWidth=110;
for(let i=0;i<r.length;i++){
 const x=r[i];
 const lines=Math.max(Math.ceil(x.target.length/44),Math.ceil(x.amount_display.length/61),Math.ceil(x.conditions_display.length/66),4);
 data.getRange(`A${i+2}:I${i+2}`).format.rowHeight=Math.min(409,Math.max(78,lines*16+16));
 if(x.notes_page_end>x.page_end){
  source.getRange(`F${i+2}`).values=[[`${x.page}–${x.notes_page_end}`]];
  source.getRange(`H${i+2}`).values=[['지급기준표와 다음 페이지의 주석을 연결하여 재검토']];
 }
}
const notes={
 A20:'보장금액 — 기준가입금액·지급단위·기간별 금액·계산식을 설명. 기준가입금액은 공시 지급표 기준이며 실제 계약금액을 적용. 단일 정액 담보는 가입금액 대비 비율도 표시.',
 A21:'보장조건 — 지급 횟수·일수 한도, 면책·감액기간, 갱신 시 예외, 차감·추가 지급 및 주요 제외사항 중심으로 정리. 다른 담보의 납입면제·계약 소멸·행정 안내는 반복하지 않음.',
 A23:'수정 검증 — 650행 및 기존 id·보험사·상품명·담보명·생성일시 유지. 원문 지급표와 다음 페이지 주석을 대조하여 핵심 지급조건과 기준금액을 확인.',
 A24:'보장대상 — 피보험자 유형과 담보별 질병·사고·치료 범위를 설명. 본인형·배우자형 및 개인·부부계약 구분은 원문 기준 유지.'
};
for(const [cell,value] of Object.entries(notes)){
 summary.getRange(cell).values=[[value]];
 summary.getRange(`${cell}:E${cell.slice(1)}`).format.rowHeight=Math.ceil(value.length/44)*17+15;
}
wb.recalculate();
console.log((await wb.inspect({kind:'table',range:'담보데이터!D36:G36',tableMaxRows:1,tableMaxCols:4,tableMaxCellChars:220,maxChars:2000})).ndjson);
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:10},summary:'final error scan',maxChars:1000})).ndjson);
for(const [sheetName,range,name,scale] of [
 ['담보데이터','E36:G37','details',1],
 ['담보데이터','E80:G81','hospital',1],
 ['처리현황','A18:E26','criteria',1.4],
 ['출처·검토','F58:H60','sources',0.8]
]){
 const blob=await wb.render({sheetName,range,scale,format:'png'});
 await fs.writeFile(`work/abl_revision/${name}.png`,new Uint8Array(await blob.arrayBuffer()));
}
await fs.mkdir('outputs/01a10ed0-eb0e-7720-80fe-23aace7c950b',{recursive:true});
const out=await SpreadsheetFile.exportXlsx(wb);
await out.save('outputs/01a10ed0-eb0e-7720-80fe-23aace7c950b/ABL생명_2507_담보분석.xlsx');
console.log('SAVED 650 rows');
