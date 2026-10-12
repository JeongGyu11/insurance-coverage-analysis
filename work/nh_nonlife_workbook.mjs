import fs from 'node:fs/promises';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const root='work/nh_nonlife',r=JSON.parse(await fs.readFile(`${root}/records.json`,'utf8')),m=JSON.parse(await fs.readFile(`${root}/manifest.json`,'utf8'));
const w=Workbook.create(),d=w.worksheets.add('담보데이터'),s=w.worksheets.add('처리현황'),p=w.worksheets.add('출처·검토');
const h=['id','company_name','product_name','coverage_name','coverage_target','coverage_amount','coverage_conditions','created_at','updated_at'],last=r.length+1;
function style(sheet,n,widths){sheet.showGridLines=false;const a=sheet.getRangeByIndexes(0,0,n,widths.length);a.format.font={name:'Malgun Gothic',size:10};a.format.wrapText=true;a.format.verticalAlignment='top';widths.forEach((v,c)=>sheet.getRangeByIndexes(0,c,n,1).format.columnWidth=v);}
function head(sheet,range){sheet.getRange(range).format={fill:'#153957',font:{name:'Malgun Gothic',size:10,bold:true,color:'#FFFFFF'},rowHeight:32,wrapText:true};}
d.getRange(`A1:I${last}`).values=[h,...r.map(x=>h.map(k=>x[k]))];style(d,last,[8,22,66,88,70,100,150,30,30]);head(d,'A1:I1');d.tables.add(`A1:I${last}`,true,'NHNonlifeCoverageData');d.freezePanes.freezeRows(1);d.freezePanes.freezeColumns(2);d.getRange(`H2:I${last}`).setNumberFormat('@');
r.forEach((x,i)=>d.getRange(`A${i+2}:I${i+2}`).format.rowHeight=Math.min(409,Math.max(100,x.coverage_conditions.split('\n').reduce((n,t)=>n+Math.ceil(t.length/105)+1,0)*14)));
style(s,32,[110,22,25]);s.getRange('A2').values=[['NH농협손해보험 · 2025년 7월 상품공시 담보 분석']];s.getRange('A2').format.font={name:'Malgun Gothic',size:15,bold:true,color:'#153957'};
const products=[...new Set(r.map(x=>x.product_name))];s.getRange('A4:C14').values=[['상품 / 형태','담보 행 수','대조 자료'],...products.map(n=>[n,r.filter(x=>x.product_name===n).length,'사업방법서·요약서·약관'])];head(s,'A4:C4');s.getRange('A5:C14').format.rowHeight=40;s.getRange('B5:B14').format.horizontalAlignment='center';
s.getRange('A16:B20').values=[['전체 담보 행 수',r.length],['상품 형태 / 원본 PDF 수','10 / 30'],['중복 제외 PDF 수',m.length],['중복 제외 약관 페이지 합계',m.filter(x=>x.kind==='약관').reduce((a,x)=>a+x.pages,0)],['분석 범위','폴더 내 2025년 7월 자료 전체']];s.getRange('A16:B20').format.rowHeight=28;
const notes=[
'분석 단위: 보험상품·담보별 한 행. 통합골절·화상·전이암·통합암·144대질병수술비 등 지급기준이 구분된 세부보장은 별도 행으로 기록. 같은 형태 내 반복 표시된 공통 담보는 중복 제외.',
'형태 구분: 다이렉트암보험 종합형·암치료집중형, 상해치료보험 일반심사·320간편심사, 펫보험 강아지 실속·일반 및 고양이 실속, 어린이보험 미지급형Ⅱ·표준형을 각각 구분. 해당 폴더에 없는 다른 형태는 제외.',
'보장금액: 계약별 보험가입금액을 고정 금액으로 추정하지 않고 지급비율·한도·횟수·감액기간 및 원문 산식을 기록. MBTI 요약서의 보험료 예시 가입금액은 실제 보장금액으로 사용하지 않음.',
'가입 제한: 어린이보험의 표준형 전용 담보는 미지급형Ⅱ에서 제외. 반려동물위탁비용은 일반형에만 반영. 반려동물 치료비는 자기부담금·보상비율·보장 대기기간 및 확장담보 합산한도를 기록.',
'원문 차이: 고양이 폴더의 사업방법서·상품요약서 파일명이 뒤바뀐 자료는 내용으로 식별. 어린이보험 요약서의 산후우울증진단비는 약관 제목인 산후우울증치료비로 기록하고 출처·검토에 차이를 남김.',
'검증: 30개 파일의 동일 내용 확인, 중복 제외 약관 3,065페이지와 요약서 지급표 추출, 담보별 약관 연결, 페이지 경계·합쳐진 셀 보정, 형별 범위·필수값·중복 및 저장 데이터 일치 검사. 주요 지급표는 시각 대조.',
'출처: 출처·검토의 id로 담보데이터와 연결. 요약서·약관 페이지는 실제 PDF 페이지 번호. 약관 연결은 담보의 관련 조항 범위이며 세부 분류표·태아 보장 조항·전체 약관도 함께 확인.',
'긴 조건: 셀 선택 후 수식 입력줄에서 전체 내용을 확인. 원문 추출의 띄어쓰기·법령 인용·예시가 일부 포함될 수 있음. 생성·수정일시는 +09:00 텍스트이며 향후 통합 시 id 재부여 필요.'
];s.getRange('A23:A30').values=notes.map(t=>[t]);notes.forEach((t,i)=>s.getRange(`A${23+i}:C${23+i}`).format.rowHeight=Math.ceil(t.length/74)*17+14);
const ph=['id','상품명','담보명','상품요약서 파일','요약서 PDF 페이지','약관 파일','약관 PDF 페이지','약관 보장명','검토사항'];
p.getRange(`A1:I${last}`).values=[ph,...r.map(x=>[x.id,x.product_name,x.coverage_name,x.summary_file,x.summary_page,x.source_file,x.source_page,x.source_name,x.review])];style(p,last,[8,66,88,110,23,110,25,88,100]);head(p,'A1:I1');p.getRange(`A2:I${last}`).format.rowHeight=145;p.tables.add(`A1:I${last}`,true,'NHNonlifeSources');p.freezePanes.freezeRows(1);
w.recalculate();console.log((await w.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!',options:{useRegex:true,maxResults:10},maxChars:500})).ndjson);
console.log((await w.inspect({kind:'table',range:'담보데이터!A1:F3',tableMaxRows:3,tableMaxCols:6,tableMaxCellChars:70,maxChars:1400})).ndjson);
for(const [sheetName,range,name] of [['담보데이터','A1:D2','data'],['담보데이터','E1:G2','details'],['처리현황','A2:C30','summary'],['출처·검토','A1:C2','sources']]){const b=await w.render({sheetName,range,scale:1.5,format:'png'});await fs.writeFile(`${root}/${name}_preview.png`,new Uint8Array(await b.arrayBuffer()));}
await (await SpreadsheetFile.exportXlsx(w)).save('outputs/NH농협손해보험_2507_담보분석.xlsx');console.log('saved',r.length);
