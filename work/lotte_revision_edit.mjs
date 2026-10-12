import fs from 'node:fs/promises';
import {SpreadsheetFile,FileBlob} from '@oai/artifact-tool';
const r=JSON.parse(await fs.readFile('work/lotte/revision/revised.json','utf8'));
const w=await SpreadsheetFile.importXlsx(await FileBlob.load('work/lotte/revision/original.xlsx'));
const d=w.worksheets.getItem('담보데이터'),s=w.worksheets.getItem('처리현황');
d.getRange('E2:G80').values=r.map(x=>[x.coverage_target,x.coverage_amount,x.coverage_conditions]);
d.getRange('I2:I80').values=r.map(x=>[x.updated_at]);
for(const [c,width] of [['E',80],['F',105],['G',160]])d.getRange(`${c}1:${c}80`).format.columnWidth=width;
r.forEach((x,i)=>{const lines=Math.max(5,Math.ceil(x.coverage_name.length/50),Math.ceil(x.coverage_target.length/46),Math.ceil(x.coverage_amount.length/63),Math.ceil(x.coverage_conditions.length/102));d.getRange(`A${i+2}:I${i+2}`).format.rowHeight=Math.min(409,Math.max(90,lines*14+15));});
const notes={A18:'보장금액: 공시 지급표 기준가입금액과 계약별 실제 가입금액을 구분하고 지급비율·단위·산식·한도를 설명. 정액 담보와 실제 손해·비용 보상을 구분하고 자기부담금 및 총한도 공유 기준을 설명.',A17:'보장대상: 피보험자의 상해·질병·치료, 사이버 피해, 주거지·휴대품 손해, 타인·반려동물 배상책임 범위를 구분. 선택특약은 가입 시 적용하며 부재·운동위험은 기존 담보 범위 확장으로 추가 보험금과 구분.',A23:'수정 검증: 기존 79행, 9개 컬럼 순서, id·보험사·상품·담보·생성일시·출처 유지. 보장조건은 지급 요건·면책·감액·횟수·한도·주요 제외 중심으로 정리. 수정일시는 +09:00 텍스트로 갱신. 긴 셀은 수식 입력줄에서 전체 확인 가능.'};
for(const [cell,value] of Object.entries(notes)){s.getRange(cell).values=[[value]];s.getRange(`${cell}:C${cell.slice(1)}`).format.rowHeight=Math.ceil(value.length/74)*17+14;}
w.recalculate();
console.log((await w.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:10},maxChars:600})).ndjson);
for(const [sheetName,range,name] of [['담보데이터','E2:G3','annuity'],['담보데이터','E5:G6','waiver'],['처리현황','A16:C23','criteria']]){const b=await w.render({sheetName,range,scale:1,format:'png'});await fs.writeFile(`work/lotte/revision/${name}.png`,new Uint8Array(await b.arrayBuffer()));}
await (await SpreadsheetFile.exportXlsx(w)).save('outputs/01a10ed0-eb0e-7720-80fe-23aace7c950b/롯데손해보험_2507_담보분석.xlsx');console.log('SAVED 79 rows');


