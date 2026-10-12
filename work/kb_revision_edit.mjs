import fs from 'node:fs/promises';
import {SpreadsheetFile,FileBlob} from '@oai/artifact-tool';
const r=JSON.parse(await fs.readFile('work/kb/revision/revised.json','utf8'));
const w=await SpreadsheetFile.importXlsx(await FileBlob.load('work/kb/revision/original.xlsx'));
const d=w.worksheets.getItem('담보데이터'),s=w.worksheets.getItem('처리현황');
d.getRange('E2:G25').values=r.map(x=>[x.coverage_target,x.coverage_amount,x.coverage_conditions]);d.getRange('I2:I25').values=r.map(x=>[x.updated_at]);
for(const [c,width] of [['E',75],['F',100],['G',110]])d.getRange(`${c}1:${c}25`).format.columnWidth=width;
r.forEach((x,i)=>{const lines=Math.max(4,Math.ceil(x.coverage_target.length/43),Math.ceil(x.coverage_amount.length/61),Math.ceil(x.coverage_conditions.length/65));d.getRange(`A${i+2}:I${i+2}`).format.rowHeight=Math.min(409,Math.max(85,lines*17+15));});
const notes={A21:'보장금액: 골든라이프는 보험가입금액 1,000만원 기준 금액·비율·배수와 감액을 설명. 월 지급 담보는 횟수·총액을 표시. 생존연금은 적립액·공시이율 산식과 보증형·미보증형 산출 기준을 구분.',A23:'별도 담보 행 제외: 제도성·보장제한 특약, 보험료 납입면제, 계약 소멸 시 적립액 반환은 새 행으로 생성하지 않음. 다른 담보의 납입면제·계약 소멸 안내는 보장조건에 반복하지 않으며 지급표 주석은 출처·검토에 보존.',A25:'수정 검증: 6개 상품 형태와 24행, 기존 id·상품·담보·생성일시·출처 유지. 보장대상은 담보별 질병·장해·생존 범위를 설명하고 조건은 면책·감액·중복 지급·횟수 및 주요 제외사항으로 정리. 원문 금액·산식 대조.'};
for(const [cell,value] of Object.entries(notes)){s.getRange(cell).values=[[value]];s.getRange(`${cell}:C${cell.slice(1)}`).format.rowHeight=Math.ceil(value.length/70)*17+14;}
w.recalculate();console.log((await w.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:10},maxChars:600})).ndjson);
for(const [sheetName,range,name] of [['담보데이터','E2:G3','accident'],['담보데이터','E4:G7','dementia'],['담보데이터','E21:G23','annuity'],['처리현황','A19:C26','criteria']]){const b=await w.render({sheetName,range,scale:1,format:'png'});await fs.writeFile(`work/kb/revision/${name}.png`,new Uint8Array(await b.arrayBuffer()));}
await (await SpreadsheetFile.exportXlsx(w)).save('outputs/01a10ed0-eb0e-7720-80fe-23aace7c950b/KB라이프생명_2507_담보분석.xlsx');console.log('SAVED 24 rows');
