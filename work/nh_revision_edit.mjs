import fs from 'node:fs/promises';
import {SpreadsheetFile,FileBlob} from '@oai/artifact-tool';
const r=JSON.parse(await fs.readFile('work/nh/revision/revised.json','utf8'));
const w=await SpreadsheetFile.importXlsx(await FileBlob.load('work/nh/revision/original.xlsx'));
const d=w.worksheets.getItem('담보데이터'),s=w.worksheets.getItem('처리현황');
d.getRange('E2:G84').values=r.map(x=>[x.coverage_target,x.coverage_amount,x.coverage_conditions]);d.getRange('I2:I84').values=r.map(x=>[x.updated_at]);
for(const [c,width] of [['E',80],['F',105],['G',110]])d.getRange(`${c}1:${c}84`).format.columnWidth=width;
r.forEach((x,i)=>{const lines=Math.max(4,Math.ceil(x.coverage_target.length/46),Math.ceil(x.coverage_amount.length/63),Math.ceil(x.coverage_conditions.length/65));d.getRange(`A${i+2}:I${i+2}`).format.rowHeight=Math.min(409,Math.max(85,lines*17+15));});
const notes={A23:'보장금액: 정액 담보는 1구좌 또는 표의 가입금액 기준·가입형별 지급액·일당·회당·장해지급률 산식을 설명. 실손 담보는 실제 본인부담 의료비와 한도·공제비율을 구분. 기준액은 개별 계약의 확정 지급액으로 추정하지 않음.',A24:'보장조건: 실손은 기본형 가입 요건, 자기부담·주요 제외, 계약 종료 후 계속치료, 한도 복원 및 다수보험 비례분담을 정리. 정액 담보는 발생 요건·최초 횟수·휴일 기준·입원 합산·미보장 가입형을 구분.',A25:'수정 검증: 2025년 7월 자료 83행(농업인 49행·온라인 34행) 및 기존 id·상품·담보·생성일시·출처 유지. 담보별 지급표·특칙과 금액·비율·지급단위·핵심 제한을 대조. 법령 설명·청구 및 분쟁 절차는 조건에 반복하지 않음.',A26:'보장대상: 자격을 충족한 피보험자의 담보별 농업작업 재해·질병·사망·장해·진단·수술·치료 범위를 설명. 생성일시는 유지하고 수정일시는 +09:00 시간대 텍스트로 갱신.'};
for(const [cell,value] of Object.entries(notes)){s.getRange(cell).values=[[value]];s.getRange(`${cell}:C${cell.slice(1)}`).format.rowHeight=Math.ceil(value.length/70)*17+14;}
w.recalculate();
console.log((await w.inspect({kind:'table',range:'담보데이터!E12:G12',tableMaxRows:1,tableMaxCols:3,tableMaxCellChars:200,maxChars:1500})).ndjson);
console.log((await w.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:10},maxChars:600})).ndjson);
for(const [sheetName,range,name] of [['담보데이터','E4:G5','disability'],['담보데이터','E12:G13','medical'],['담보데이터','E78:G79','riders'],['처리현황','A19:C26','criteria']]){const b=await w.render({sheetName,range,scale:1,format:'png'});await fs.writeFile(`work/nh/revision/${name}.png`,new Uint8Array(await b.arrayBuffer()));}
await (await SpreadsheetFile.exportXlsx(w)).save('outputs/01a10ed0-eb0e-7720-80fe-23aace7c950b/NH농협생명_2507_담보분석.xlsx');console.log('SAVED 83 rows');
