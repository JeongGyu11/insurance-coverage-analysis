import fs from 'node:fs/promises';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const root='work/heungkuk',r=JSON.parse(await fs.readFile(root+'/records.json','utf8')),m=JSON.parse(await fs.readFile(root+'/manifest.json','utf8')),pending=JSON.parse(await fs.readFile(root+'/pending_ids.json','utf8'));
const w=Workbook.create(),d=w.worksheets.add('담보데이터'),s=w.worksheets.add('처리현황'),p=w.worksheets.add('출처·검토'),v=w.worksheets.add('추가대조항목'),last=r.length+1;
const h=['id','company_name','product_name','coverage_name','coverage_target','coverage_amount','coverage_conditions','created_at','updated_at'];
function style(sh,n,ws){sh.showGridLines=false;sh.getRangeByIndexes(0,0,n,ws.length).format.font={name:'Malgun Gothic',size:10};sh.getRangeByIndexes(0,0,n,ws.length).format.wrapText=true;sh.getRangeByIndexes(0,0,n,ws.length).format.verticalAlignment='top';ws.forEach((x,c)=>sh.getRangeByIndexes(0,c,n,1).format.columnWidth=x);}
function head(sh,range){sh.getRange(range).format={fill:'#153957',font:{name:'Malgun Gothic',size:10,bold:true,color:'#FFFFFF'},rowHeight:34,wrapText:true};}
d.getRange('A1:I'+last).values=[h,...r.map(x=>h.map(k=>x[k]))];style(d,last,[8,18,68,83,84,102,126,28,28]);head(d,'A1:I1');d.tables.add('A1:I'+last,true,'HeungkukCoverage');d.freezePanes.freezeRows(1);d.freezePanes.freezeColumns(2);d.getRange('H2:I'+last).setNumberFormat('@');
r.forEach((x,i)=>{d.getRange('A'+(i+2)+':I'+(i+2)).format.rowHeight=Math.min(409,Math.max(88,Math.ceil(Math.max(x.coverage_name.length/50,x.coverage_target.length/49,x.coverage_amount.length/60,x.coverage_conditions.length/73))*17+20));if(pending.includes(x.id))d.getRange('D'+(i+2)).format.fill='#FFF1CC';});
style(s,86,[95,15,32,105]);s.getRange('A2').values=[['흥국화재 · 2025년 7월 공시 담보 분석']];s.getRange('A2').format.font={name:'Malgun Gothic',size:15,bold:true,color:'#153957'};
const products=[...new Set(r.map(x=>x.product_name))],status=[['상품명','담보 행 수','약관 추가 대조','비고'],...products.map(n=>[n,r.filter(x=>x.product_name===n).length,r.filter(x=>x.product_name===n&&pending.includes(x.id)).length,n.includes('실손')?'급여·비급여 및 입원·통원·상급병실료 지급구조 구분.':n.includes('2종')?'종별 구분을 유지하고 갱신형의 최초계약 감액과 재갱신을 구분.':'원문 지급표의 보장구조·가입금액·횟수·기간 구분.']),['실손의료비보장 안정화 할인Ⅲ(25.07) 특별약관',0,0,'보험료 할인제도. 독립적인 보험금 지급담보를 추가하지 않음.']];
s.getRange('A4:D'+(status.length+3)).values=status;head(s,'A4:D4');s.getRange('A5:D'+(status.length+3)).format.rowHeight=64;
s.getRange('A23:B26').values=[['전체 담보 행 수',r.length],['자료 폴더 / PDF 수','16 / 47'],['상품요약서에 근거한 추가 약관 대조 항목',pending.length],['공시 기준','폴더 내 2025년 7월 PDF 전체']];s.getRange('A23:B26').format.rowHeight=30;
const notes=[
'담보데이터는 요청한 9개 컬럼 순서를 유지합니다. 하나의 행은 해당 상품의 담보·지급구조를 나타냅니다. 선택 가능 가입금액별로 가상의 금액을 만들지 않고 가입금액 대비 비율·일당·회당·세부보장 및 실손 산식을 기록합니다.',
'보장대상에는 피보험자·질환·상해·치료·의료기관 범위를 설명합니다. 조건에는 면책·감액·횟수·기간·중복 지급·실제 치료 요건을 남기고 불필요한 특약 가입 안내 문구를 넣지 않습니다. 지급조건이 따로 제시되지 않은 경우 선택 컬럼을 빈칸으로 두었습니다.',
'상품요약서의 1종·2종 공유 파일은 파일 해시로 중복을 확인해 추출을 재사용하되 상품명과 각각의 약관 출처를 유지했습니다. 동일 담보명·보장대상·금액이 반복된 표는 한 번만 기록하고 금액 구조가 다른 항목은 구분했습니다.',
'실손보험은 6개 일반형 상품과 유병력자 1개 상품을 각각 작성했습니다. 일반형 급여 20%·비급여 30% 공제, 통원 정액 공제 및 가입금액별 한도를 구분했습니다. 3대 비급여의 연간 한도·횟수와 도수치료 추가 인정 조건을 기록했습니다.',
'주의할 원문 표기: 일부 요약서 담보명은 약관 제목과 일치하지 않거나 분류 라벨이 붙어 있습니다. 직접 대응을 확정하기 어려운 '+pending.length+'행은 요약서 지급표에 명시된 값만 기록하고 추가대조항목 시트와 담보명 연한 노랑으로 표시했습니다. 이 행에는 비슷한 다른 특약의 약관 조건을 임의 적용하지 않았습니다.',
'실손 안정화 할인Ⅲ는 보험료 할인 특별약관으로 보험금 지급행을 만들지 않았습니다. 청구대리·세제·계약전환·보장제한 등 제도성 특약과 공통 행정 절차는 별도 현금 지급담보로 추가하지 않습니다.',
'출처·검토의 id로 근거 문서와 실제 PDF 페이지를 추적할 수 있습니다. 추가대조항목의 원문 근거는 상품요약서 지급표이며, 다른 행은 개별 약관 연결을 우선 기록했습니다. id는 파일 내 연속번호로 DB 적재 시 DB 자동 생성 정책을 적용합니다. 생성·수정일시는 +09:00 포함 텍스트입니다.'
];s.getRange('A29:A35').values=notes.map(x=>[x]);notes.forEach((x,i)=>{s.getRange('A'+(29+i)+':D'+(29+i)).merge();s.getRange('A'+(29+i)+':D'+(29+i)).format.rowHeight=Math.ceil(x.length/125)*18+25;});
s.getRange('A38:D85').values=[['원본 폴더','종류','PDF 페이지','원본 파일'],...m.map(x=>[x.product,x.kind,x.pages,x.path])];head(s,'A38:D38');s.getRange('A39:D85').format.rowHeight=68;
const ph=['id','상품명','담보명','근거 문서','근거 PDF 페이지','상품요약서','요약서 PDF 페이지','검토상태','검토내용'];p.getRange('A1:I'+last).values=[ph,...r.map(x=>[x.id,x.product_name,x.coverage_name,x.source_file,x.source_page,x.summary_file,x.summary_page,pending.includes(x.id)?'약관 추가 대조':'원문 연결',x.review])];style(p,last,[8,68,83,112,22,112,22,25,88]);head(p,'A1:I1');p.getRange('A2:I'+last).format.rowHeight=92;p.tables.add('A1:I'+last,true,'HeungkukSource');p.freezePanes.freezeRows(1);
const vr=r.filter(x=>pending.includes(x.id));v.getRange('A1:F'+(vr.length+1)).values=[['id','상품명','담보명','상품요약서','PDF 페이지','확인할 내용'],...vr.map(x=>[x.id,x.product_name,x.coverage_name,x.summary_file,x.summary_page,'상품요약서와 약관의 같은 담보 제목·가입형 및 지급구조를 추가 대조. 요약서 금액을 추정으로 대체하지 않음.'])];style(v,vr.length+1,[8,68,83,115,22,100]);head(v,'A1:F1');v.getRange('A2:F'+(vr.length+1)).format.rowHeight=100;v.freezePanes.freezeRows(1);v.tables.add('A1:F'+(vr.length+1),true,'HeungkukReview');
w.recalculate();console.log((await w.inspect({kind:'table',range:'처리현황!A23:B26',include:'values',tableMaxRows:4,tableMaxCols:2,maxChars:900})).ndjson);
console.log((await w.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!',options:{useRegex:true,maxResults:8},maxChars:500})).ndjson);
for(const [sheetName,range,name] of [['처리현황','A4:D10','summary'],['담보데이터','E3:G5','details'],['담보데이터','E2074:G2076','medical'],['추가대조항목','A1:C4','review']]){const b=await w.render({sheetName,range,scale:1,format:'png'});await fs.writeFile(root+'/'+name+'_preview.png',new Uint8Array(await b.arrayBuffer()));}
await (await SpreadsheetFile.exportXlsx(w)).save('outputs/01a10ed0-eb0e-7720-80fe-23aace7c950b/흥국화재_2507_담보분석.xlsx');console.log('SAVED',r.length);

