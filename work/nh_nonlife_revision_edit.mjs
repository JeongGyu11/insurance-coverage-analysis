import fs from 'node:fs/promises';
import {SpreadsheetFile,FileBlob} from '@oai/artifact-tool';
const r=JSON.parse(await fs.readFile('work/nh_nonlife/revision/revised.json','utf8'));
const w=await SpreadsheetFile.importXlsx(await FileBlob.load('work/nh_nonlife/revision/original.xlsx'));
const d=w.worksheets.getItem('담보데이터'),s=w.worksheets.getItem('처리현황');
d.getRange('E2:G749').values=r.map(x=>[x.coverage_target,x.coverage_amount,x.coverage_conditions]);d.getRange('I2:I749').values=r.map(x=>[x.updated_at]);
for(const [c,width] of [['E',80],['F',105],['G',160]])d.getRange(`${c}1:${c}749`).format.columnWidth=width;
r.forEach((x,i)=>{const lines=Math.max(5,Math.ceil(x.coverage_name.length/50),Math.ceil(x.coverage_target.length/46),Math.ceil(x.coverage_amount.length/63),Math.ceil(x.coverage_conditions.length/102));d.getRange(`A${i+2}:I${i+2}`).format.rowHeight=Math.min(409,Math.max(90,lines*14+15));});
const notes={A25:'보장금액: 증권상 가입금액·지급비율·단위·횟수·한도와 손해액 산식을 설명. 반려동물 치료비·배상책임·비용 보장은 실제 손해와 한도를 구분. 보험료 납입면제는 보험금 대신 면제 범위를 설명.',A28:'수정 검증: 상품 형태 10개와 기존 748행, id·보험사·상품·담보·생성일시·출처 유지. 원문 지급액·비율·단위와 핵심 제한을 대조. 기본계약과 특약, 상품별 가입 범위를 구분.',A30:'보장대상·조건: 담보별 질병·상해·장해·치료·산모·부양자·반려동물·배상책임 범위를 설명. 조건은 지급 요건·면책·감액·횟수·한도·주요 제외 중심으로 정리. 법령 설명·분쟁 및 청구 절차를 줄임. 긴 셀은 수식 입력줄에서 전체 확인 가능. 생성일시는 유지하고 수정일시는 +09:00 텍스트로 갱신.'};
for(const [cell,value] of Object.entries(notes)){s.getRange(cell).values=[[value]];s.getRange(`${cell}:C${cell.slice(1)}`).format.rowHeight=Math.ceil(value.length/74)*17+14;}
w.recalculate();
console.log((await w.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:10},maxChars:600})).ndjson);
for(const [sheetName,range,name] of [['담보데이터','E9:G10','cancer'],['담보데이터','E70:G71','pet'],['담보데이터','E748:G749','liability'],['처리현황','A23:C30','criteria']]){const b=await w.render({sheetName,range,scale:1,format:'png'});await fs.writeFile(`work/nh_nonlife/revision/${name}.png`,new Uint8Array(await b.arrayBuffer()));}
await (await SpreadsheetFile.exportXlsx(w)).save('outputs/01a10ed0-eb0e-7720-80fe-23aace7c950b/NH농협손해보험_2507_담보분석.xlsx');console.log('SAVED 748 rows');
