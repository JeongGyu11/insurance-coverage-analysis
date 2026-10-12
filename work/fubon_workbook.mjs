import fs from 'node:fs/promises';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const root='work/fubon',r=JSON.parse(await fs.readFile(`${root}/records.json`,'utf8')),m=JSON.parse(await fs.readFile(`${root}/manifest.json`,'utf8'));
const w=Workbook.create(),d=w.worksheets.add('담보데이터'),s=w.worksheets.add('처리현황'),p=w.worksheets.add('출처·검토'),last=r.length+1;
const h=['id','company_name','product_name','coverage_name','coverage_target','coverage_amount','coverage_conditions','created_at','updated_at'];
function style(sh,n,widths){sh.showGridLines=false;const a=sh.getRangeByIndexes(0,0,n,widths.length);a.format.font={name:'Malgun Gothic',size:10};a.format.wrapText=true;a.format.verticalAlignment='top';widths.forEach((v,c)=>sh.getRangeByIndexes(0,c,n,1).format.columnWidth=v);}
function head(sh,range){sh.getRange(range).format={fill:'#153957',font:{name:'Malgun Gothic',size:10,bold:true,color:'#FFFFFF'},rowHeight:32,wrapText:true};}
d.getRange(`A1:I${last}`).values=[h,...r.map(x=>h.map(k=>x[k]))];style(d,last,[8,20,60,78,86,98,138,29,29]);head(d,'A1:I1');d.tables.add(`A1:I${last}`,true,'FubonCoverageData');d.freezePanes.freezeRows(1);d.freezePanes.freezeColumns(2);d.getRange(`H2:I${last}`).setNumberFormat('@');
r.forEach((x,i)=>d.getRange(`A${i+2}:I${i+2}`).format.rowHeight=Math.min(409,Math.max(105,Math.ceil(Math.max(x.coverage_name.length/44,x.coverage_target.length/50,x.coverage_amount.length/56,x.coverage_conditions.length/80))*18+25)));
style(s,43,[95,18,30,110]);s.getRange('A2').values=[['푸본현대생명 · 2025년 7월 공시 담보 분석']];s.getRange('A2').format.font={name:'Malgun Gothic',size:15,bold:true,color:'#153957'};
const products=[...new Set(r.map(x=>x.product_name))];s.getRange('A4:D9').values=[['상품명','담보 행 수','처리','검토사항'],...products.map(n=>[n,r.filter(x=>x.product_name===n).length,'분석 완료',n.startsWith('MAX')?'체증형 사망·연금선지급·연금전환 및 사망보험금 지급제도 구분.':n.includes('간편가입')?'주계약·선택특약·보험료납입면제와 사망보험금 지급제도 분석.':'일반가입 전용 대사질환 특약 및 진단특약 기본형·집중보장형 구분.'])];head(s,'A4:D4');s.getRange('A5:D9').format.rowHeight=75;
s.getRange('A11:B13').values=[['전체 담보 행 수',r.length],['상품 폴더 / PDF 수','5 / 10'],['약관 페이지 합계',m.filter(x=>x.kind==='약관').reduce((a,x)=>a+x.pages,0)]];s.getRange('A11:B13').format.rowHeight=30;
s.getRange('A15:D25').values=[['원본 폴더','문서 종류','PDF 페이지','원본 파일'],...m.map(x=>[x.product,x.kind,x.pages,x.path])];head(s,'A15:D15');s.getRange('A16:D25').format.rowHeight=80;
const notes=[
'분석 범위: 푸본현대생명_2507의 2025년 7월 공시 폴더 5개, PDF 10개 전체. 약관 표지의 실제 개정표시는 건강보험 2504, 종신보험 2505이며 이를 다른 시점 자료로 임의 교체하지 않음. 담보데이터는 요청한 9개 컬럼 순서를 유지.',
'DB 예시 적용: 보장대상에는 피보험자·대상 질환·치료 및 기관 범위를 설명하고, 보장금액은 가입금액 대비 비율·회당/일당/월 지급·변동 산식 및 정액을 구분. 조건은 면책·감액·횟수·기간·중복 지급·허가치료 요건 위주로 작성. 청구서류와 분쟁 절차는 반복하지 않음.',
'지급표 예시와 실제 금액: 보험가입금액 500만원·1,000만원 등을 기준으로 한 예시 금액을 실제 계약의 고정금액으로 보지 않음. 해당 계약 가입금액에 지급비율을 적용. 연금전환 재해장해 월 50만원×36회는 약관에 정액으로 표시된 보장. 주계약 사망은 가입금액과 이미 납입한 보험료 중 큰 금액.',
'일반형과 플러스형: 동일 가입방식의 특약 본문 전 페이지가 동일함을 대조. 폴더별 상품명·원본 파일을 유지했으므로 통합 DB에서 상품명을 정규화할 때 동일 특약 지급내용의 중복 여부를 검토할 수 있음. 일반가입형에는 고혈압·당뇨병·이상지질혈증 등의 별도 특약이 있음.',
'집중보장형: 일반가입 비갱신 암·뇌혈관질환·허혈성심장질환 진단특약은 기본형과 집중보장형을 따로 작성. 집중보장형은 계약일부터 10년 경과 전 가입금액 100%, 10년 경과 계약해당일부터 200%. 뇌혈관·허혈성의 집중보장배수는 약관 정의상 2배.',
'지급제도·면제 구분: 보험료납입면제는 현금 보험금이 아님을 명시. 사후정리와 선지급서비스는 기존 사망보험금의 지급방식으로 별도 추가 보장액을 합산하지 않음. MAX 사망보험금 연금선지급금은 감액분 해약환급금이며 사망보험금을 단순 분할한 금액이 아님.',
'검토 제외: 장애인전용보험전환·지정대리청구·특별조건부·특정 신체부위/질병 보장제한부 인수 특약은 세제·청구·인수 조건을 정하는 제도성 특약으로 독립 지급담보를 추가하지 않음. 용어해설·법규·상품코드는 보조자료. 담보데이터에 공시되지 않은 보장금액을 추정해 넣지 않음.',
'출처 확인: 출처·검토 시트 id로 원문 약관과 실제 PDF 페이지를 추적. 약관 인쇄 페이지와 PDF 페이지는 다르며 출처에는 실제 PDF 페이지를 사용. 지급기준표 표 구조·병합 셀·주요 조건 및 이미지 표본을 대조. 생성/수정일시는 +09:00 포함 ISO 텍스트이며 id는 이 파일 내 1부터 연속 부여. DB 적재 시에는 DB 자동 생성 id·일시 정책 적용.'
];s.getRange('A28:A35').values=notes.map(v=>[v]);notes.forEach((v,i)=>{s.getRange(`A${i+28}:D${i+28}`).merge();s.getRange(`A${i+28}:D${i+28}`).format.rowHeight=Math.ceil(v.length/150)*20+30;});
const ph=['id','상품명','담보명','약관 파일','약관 PDF 페이지','사업방법서 파일','검토 범위','검토내용'];p.getRange(`A1:H${last}`).values=[ph,...r.map(x=>[x.id,x.product_name,x.coverage_name,x.source_file,x.source_page,x.business_file,x.business_page,x.review])];style(p,last,[8,60,78,115,24,115,20,90]);head(p,'A1:H1');p.getRange(`A2:H${last}`).format.rowHeight=110;p.tables.add(`A1:H${last}`,true,'FubonCoverageSources');p.freezePanes.freezeRows(1);
w.recalculate();console.log((await w.inspect({kind:'table',range:'처리현황!A4:D9',include:'values',tableMaxRows:6,tableMaxCols:4,maxChars:1700})).ndjson);
console.log((await w.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!',options:{useRegex:true,maxResults:10},maxChars:500})).ndjson);
for(const [sheetName,range,name] of [['처리현황','A4:D13','summary'],['담보데이터','E8:G10','care'],['담보데이터','E138:G140','focus']]){const b=await w.render({sheetName,range,scale:1,format:'png'});await fs.writeFile(`${root}/${name}_preview.png`,new Uint8Array(await b.arrayBuffer()));}
await (await SpreadsheetFile.exportXlsx(w)).save('outputs/01a10ed0-eb0e-7720-80fe-23aace7c950b/푸본현대생명_2507_담보분석.xlsx');console.log('SAVED',r.length);
