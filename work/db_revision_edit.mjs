import fs from 'node:fs/promises';
import {SpreadsheetFile,FileBlob} from '@oai/artifact-tool';
const r=JSON.parse(await fs.readFile('work/db/revision/revised.json','utf8'));
const w=await SpreadsheetFile.importXlsx(await FileBlob.load('work/db/revision/original.xlsx'));
const d=w.worksheets.getItem('담보데이터'),s=w.worksheets.getItem('처리현황'),p=w.worksheets.getItem('출처·검토');
d.getRange('E2:G20').values=r.map(x=>[x.coverage_target,x.coverage_amount,x.coverage_conditions]);
d.getRange('I2:I20').values=r.map(x=>[x.updated_at]);
for(const [c,width] of [['E',75],['F',95],['G',110]])d.getRange(`${c}1:${c}20`).format.columnWidth=width;
r.forEach((x,i)=>{const lines=Math.max(4,Math.ceil(x.coverage_target.length/43),Math.ceil(x.coverage_amount.length/56),Math.ceil(x.coverage_conditions.length/65));d.getRange(`A${i+2}:I${i+2}`).format.rowHeight=Math.max(85,lines*17+15);});
for(const [id,page] of [[11,123],[12,124],[14,127]]){
 const x=r[id-1];p.getRange(`H${id+1}`).values=[[x.review+`; 보장범위 설명은 약관 질병 분류표 PDF ${page}페이지 추가 확인`]];
}
const notes={
 A19:'보장금액: 공시 보험가입금액 1,000만원 기준 금액과 가입금액 대비 지급비율·배수·산식·지급단위를 설명. 실제 계약가입금액을 적용하며 대상포진·통풍의 1년 미만 50% 감액을 표시.',
 A22:'수정 검증: 19행과 기존 id·보험사·상품·담보·생성일시 유지. 지급기준표 3개 및 장해·수술·질병 분류표를 대조. 출처·검토의 id로 연결하며 PDF 실제 페이지 번호를 사용.',
 A23:'보장대상·조건: 보장대상에는 담보별 질병·재해·진단·수술 범위를 설명. 보장조건은 최초·연간 횟수, 감액, 장해 판정·차감, 추가 지급과 주요 제외사항 중심으로 정리.'
};
for(const [cell,value] of Object.entries(notes)){s.getRange(cell).values=[[value]];s.getRange(`${cell}:C${cell.slice(1)}`).format.rowHeight=Math.ceil(value.length/58)*17+14;}
w.recalculate();
console.log((await w.inspect({kind:'table',range:'담보데이터!E2:G2',tableMaxRows:1,tableMaxCols:3,tableMaxCellChars:180,maxChars:1600})).ndjson);
console.log((await w.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:10},maxChars:600})).ndjson);
for(const [sheetName,range,name] of [['담보데이터','E2:G4','details'],['담보데이터','E14:G16','health'],['처리현황','A17:C24','criteria'],['출처·검토','H12:I15','sources']]){
 const b=await w.render({sheetName,range,scale:1,format:'png'});await fs.writeFile(`work/db/revision/${name}.png`,new Uint8Array(await b.arrayBuffer()));
}
await (await SpreadsheetFile.exportXlsx(w)).save('outputs/01a10ed0-eb0e-7720-80fe-23aace7c950b/DB생명_2507_담보분석.xlsx');
console.log('SAVED 19 rows');
