import fs from 'node:fs/promises';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const root='work/nh',r=JSON.parse(await fs.readFile(`${root}/records.json`,'utf8'));
const w=Workbook.create(),d=w.worksheets.add('담보데이터'),s=w.worksheets.add('처리현황'),p=w.worksheets.add('출처·검토');
const h=['id','company_name','product_name','coverage_name','coverage_target','coverage_amount','coverage_conditions','created_at','updated_at'],last=r.length+1;
function style(sheet,n,widths){sheet.showGridLines=false;const a=sheet.getRangeByIndexes(0,0,n,widths.length);a.format.font={name:'Malgun Gothic',size:10};a.format.wrapText=true;a.format.verticalAlignment='top';widths.forEach((v,c)=>sheet.getRangeByIndexes(0,c,n,1).format.columnWidth=v);}
function head(sheet,range){sheet.getRange(range).format={fill:'#153957',font:{name:'Malgun Gothic',size:10,bold:true,color:'#FFFFFF'},rowHeight:32,wrapText:true};}
d.getRange(`A1:I${last}`).values=[h,...r.map(x=>h.map(k=>x[k]))];style(d,last,[8,20,48,80,80,105,150,30,30]);head(d,'A1:I1');d.tables.add(`A1:I${last}`,true,'NHCoverageData');d.freezePanes.freezeRows(1);d.freezePanes.freezeColumns(2);d.getRange(`H2:I${last}`).setNumberFormat('@');
r.forEach((x,i)=>d.getRange(`A${i+2}:I${i+2}`).format.rowHeight=Math.min(409,Math.max(110,x.coverage_conditions.split('\n').reduce((n,t)=>n+Math.ceil(t.length/105)+1,0)*14)));
style(s,28,[105,22,32]);s.getRange('A2').values=[['NH농협생명 · 2025년 7월 상품공시 담보 분석']];s.getRange('A2').format.font={name:'Malgun Gothic',size:15,bold:true,color:'#153957'};
const groups=[['농업인NH안전보험(무배당)','일반형(1·2·3형)'],['농업인NH안전보험(무배당)','산재형'],['농업인NH안전보험(무배당)','휴일보장형'],['농업인NH안전보험(무배당)','특약'],['온라인농업인NH안전보험(무배당)','일반 1형'],['온라인농업인NH안전보험(무배당)','산재형']];
s.getRange('A4:C10').values=[['상품 / 보장형','담보 행 수','검토 기준'],...groups.map(([prod,type])=>[prod+' · '+type,r.filter(x=>x.product_name===prod&&(type==='특약'?!x.type.endsWith('주계약'):x.type===type+' · 주계약')).length,type==='특약'?'5개 특약 / 7개 지급 담보':type==='휴일보장형'?'휴일 기준 담보 8개':'정액 담보 + 치료급여금 세부보장'])];head(s,'A4:C4');s.getRange('A5:C10').format.rowHeight=45;s.getRange('B5:B10').format.horizontalAlignment='center';
s.getRange('A12:B16').values=[['전체 담보 행 수',83],['상품 수',2],['선택 범위','2025년 7월 폴더만'],['선택 원본 PDF / 중복 제외 PDF','6 / 4'],['약관 페이지 합계',384]];s.getRange('A12:B16').format.rowHeight=28;
const notes=[
'범위: 사용자의 중간 확인에 따라 2025년 7월 자료만 분석. 농업인NH안전보험 49개, 온라인농업인NH안전보험 34개. 2024년 및 다른 월·연도 자료는 결과에서 제외.',
'행 구성: 일반형의 1·2·3형 금액은 동일 담보 행 안에 구분 표기. 일반 3형에서 보장하지 않는 재해장해·재활(재해장해)은 보장금액과 조건에 명시.',
'치료급여금: 상해입원, 상해통원(외래·처방조제), 질병입원, 질병통원, 비급여 도수·체외충격파·증식치료, 비급여 주사료, 비급여 MRI/MRA의 7개 보장으로 분리. 부모 담보는 중복 생성하지 않음.',
'온라인 제한: 공통 사업방법서상 사이버몰은 일반 1형·산재형, 만 19세 이상으로 가입하며 특약을 부가하지 않음. 온라인 약관에 표시된 다른 형의 공통 지급표를 온라인 판매 담보로 추가하지 않음.',
'보장금액: 정액 급부는 지급표의 1구좌 기준. 장제비지원특약은 가입금액 100만원 기준이며 계약별로 100·300·500만원 운용. 재해골절·깁스치료 특약은 가입금액 10만원 기준. 실손 보장은 원문 한도·공제·비율을 기록.',
'의료비 조건: 기본형 가입 시에만 치료급여금 보장. 부(不)담보형에서는 제외. 실손 조항의 자기부담·보상 제외·계약 종료 후 치료·한도 복원 기준을 기록했으며 다수보험은 약관 제52조 및 사업방법서의 비례분담 기준 적용.',
'출처: 개별 약관과 공통 상품요약서·사업방법서를 대조. 출처·검토의 id로 연결하며 모든 페이지는 실제 PDF 페이지 번호. 긴 조건은 셀 선택 후 수식 입력줄에서 전체 확인 가능. 상세 분류표와 전체 약관을 함께 확인.',
'생성·수정일시는 +09:00 시간대 포함 텍스트. 통합할 때 id 재부여 필요. 원문 추출에 따른 띄어쓰기 차이가 남아 있으며 법령 인용·예시가 일부 조건에 포함됨.'
];s.getRange('A19:A26').values=notes.map(t=>[t]);notes.forEach((t,i)=>s.getRange(`A${19+i}:C${19+i}`).format.rowHeight=Math.ceil(t.length/70)*17+14);
const ph=['id','상품명','담보명','약관 파일','지급표 / 특칙 PDF 페이지','관련 본문 PDF 페이지','공통 참고 자료','검토사항'];
const inv=JSON.parse(await fs.readFile(`${root}/inventory.json`,'utf8'));
p.getRange(`A1:H${last}`).values=[ph,...r.map(x=>[x.id,x.product_name,x.coverage_name,x.source_file,x.source_page,x.article_pages,inv.filter(y=>y.kind!=='약관'&&y.product_folder===inv.find(y=>y.path===x.source_file).product_folder).map(y=>y.path).join('\n'),x.review])];style(p,last,[8,48,80,110,26,28,110,85]);head(p,'A1:H1');p.getRange(`A2:H${last}`).format.rowHeight=145;p.tables.add(`A1:H${last}`,true,'NHSources');p.freezePanes.freezeRows(1);
w.recalculate();console.log((await w.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!',options:{useRegex:true,maxResults:10},maxChars:500})).ndjson);
console.log((await w.inspect({kind:'table',range:'담보데이터!A1:F3',tableMaxRows:3,tableMaxCols:6,tableMaxCellChars:80,maxChars:1500})).ndjson);
for(const [sheetName,range,name] of [['담보데이터','A1:D2','data'],['담보데이터','E1:G2','details'],['처리현황','A2:C26','summary'],['출처·검토','A1:C2','sources']]){const b=await w.render({sheetName,range,scale:1.5,format:'png'});await fs.writeFile(`${root}/${name}_preview.png`,new Uint8Array(await b.arrayBuffer()));}
await (await SpreadsheetFile.exportXlsx(w)).save('outputs/NH농협생명_2507_담보분석.xlsx');console.log('saved 83 rows');
