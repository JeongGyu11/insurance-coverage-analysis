import fs from 'node:fs/promises';
import {SpreadsheetFile,FileBlob} from '@oai/artifact-tool';
const r=JSON.parse(await fs.readFile('work/kyobo/revision/revised.json','utf8'));
const w=await SpreadsheetFile.importXlsx(await FileBlob.load('work/kyobo/revision/original.xlsx'));
const d=w.worksheets.getItem('담보데이터'),s=w.worksheets.getItem('처리현황');
d.getRange('E2:G284').values=r.map(x=>[x.coverage_target,x.coverage_amount,x.coverage_conditions]);
d.getRange('I2:I284').values=r.map(x=>[x.updated_at]);
for(const [c,width] of [['E',80],['F',105],['G',160]])d.getRange(`${c}1:${c}284`).format.columnWidth=width;
r.forEach((x,i)=>{const lines=Math.max(5,Math.ceil(x.coverage_name.length/50),Math.ceil(x.coverage_target.length/46),Math.ceil(x.coverage_amount.length/63),Math.ceil(x.coverage_conditions.length/102));d.getRange(`A${i+2}:I${i+2}`).format.rowHeight=Math.min(409,Math.max(90,lines*14+15));});
const notes={A21:'보장금액: 공시 지급표 기준가입금액과 계약별 실제 가입금액을 구분하고 지급비율·단위·산식·한도를 설명. 연금은 적립액 및 약정 지급형태를, 납입면제는 현금 지급 대신 면제 범위를 설명.',A22:'보장대상: 피보험자와 질병·재해·장해·치료·생존 등 담보별 범위를 설명. 선택형·갱신형·전환계약·납입면제 1~5형은 해당 계약 형태에 적용되는 요건을 구분.',A26:'수정 검증: 기존 283행, 9개 컬럼 순서, id·보험사·상품·담보·생성일시·출처 유지. 보장조건은 지급 요건·면책·감액·횟수·한도·주요 제외 중심으로 정리. 수정일시는 +09:00 텍스트로 갱신. 긴 셀은 수식 입력줄에서 전체 확인 가능.'};
for(const [cell,value] of Object.entries(notes)){s.getRange(cell).values=[[value]];s.getRange(`${cell}:C${cell.slice(1)}`).format.rowHeight=Math.ceil(value.length/74)*17+14;}
w.recalculate();
console.log((await w.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:10},maxChars:600})).ndjson);
for(const [sheetName,range,name] of [['담보데이터','E2:G3','annuity'],['담보데이터','E249:G250','waiver'],['처리현황','A19:C26','criteria']]){const b=await w.render({sheetName,range,scale:1,format:'png'});await fs.writeFile(`work/kyobo/revision/${name}.png`,new Uint8Array(await b.arrayBuffer()));}
await (await SpreadsheetFile.exportXlsx(w)).save('outputs/01a10ed0-eb0e-7720-80fe-23aace7c950b/교보생명_2507_담보분석.xlsx');console.log('SAVED 283 rows');
