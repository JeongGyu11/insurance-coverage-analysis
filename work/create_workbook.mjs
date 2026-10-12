import fs from 'node:fs/promises';
import path from 'node:path';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const rec=JSON.parse(await fs.readFile('work/records.json','utf8'));
const files=JSON.parse(await fs.readFile('work/files.json','utf8'));
const counts=JSON.parse(await fs.readFile('work/counts.json','utf8'));
const business=JSON.parse(await fs.readFile('work/business.json','utf8'));
const wb=Workbook.create();
const sheet=wb.worksheets.add('담보데이터'),summary=wb.worksheets.add('처리현황'),source=wb.worksheets.add('출처·검토');
const header=['id','company_name','product_name','coverage_name','coverage_target','coverage_amount','coverage_conditions','created_at','updated_at'];
function sectionShort(r){let x=r.section.replace(/^무배당\s*/,'').trim();if(x.startsWith('ABL'))return '주계약'+(x.includes('간편심사형')?'·간편심사형':x.includes('일반심사형')?'·일반심사형':'');return x;}
const data=rec.map(r=>[r.id,'ABL생명',r.product,`${r.name} [${sectionShort(r)}]`,r.target,(r.basis?`[${r.basis}]\n`:'')+r.amount,r.conditions,r.created_at.replace('T',' '),r.updated_at.replace('T',' ')]);
sheet.getRange(`A1:I${data.length+1}`).values=[header,...data];
const table=sheet.tables.add(`A1:I${data.length+1}`,true,'CoverageData');table.showFilterButton=true;
function base(s,range,widths){s.showGridLines=false;s.getRange(range).format.font={name:'Malgun Gothic',size:10};s.getRange(range).format.verticalAlignment='top';s.getRange(range).format.wrapText=true;for(let i=0;i<widths.length;i++)s.getRangeByIndexes(0,i,range==='A1:I651'?651:range.startsWith('A1:H')?651:50,1).format.columnWidth=widths[i];}
base(sheet,`A1:I${data.length+1}`,[8,14,42,58,65,85,170,29,29]);
sheet.getRange('A1:I1').format={fill:'#153957',font:{name:'Malgun Gothic',size:10,bold:true,color:'#FFFFFF'},rowHeight:30,wrapText:false};
sheet.getRange(`A2:A${data.length+1}`).setNumberFormat('0');sheet.getRange(`H2:I${data.length+1}`).setNumberFormat('@');
for(let i=0;i<data.length;i++){
 const r=data[i];const chars=[0,0,28,39,44,58,119,0,0];let lines=3;
 for(let k=2;k<=6;k++)lines=Math.max(lines,...String(r[k]).split('\n').map(t=>Math.ceil(t.length/chars[k])+1));
 // Long source conditions stay intact; row height is bounded by Excel's native limit.
 sheet.getRange(`A${i+2}:I${i+2}`).format.rowHeight=Math.min(409,Math.max(72,lines*15+12));
}
sheet.freezePanes.freezeRows(1);sheet.freezePanes.freezeColumns(2);sheet.tabColor='#153957';
const per=counts.map((c,d)=>{const file=files.find(f=>f.path===c.file);return{d,product:rec.find(r=>r.doc===d).product,n:rec.filter(r=>r.doc===d).length,pages:c.pages,hash:file.hash,duplicates:files.filter(f=>f.hash===file.hash&&f.path!==file.path).map(f=>f.path)};});
summary.getRange('A2').values=[['ABL생명 상품공시 담보 분석']];summary.getRange('A2').format.font={name:'Malgun Gothic',size:14,bold:true,color:'#153957'};
summary.getRange('A4:E8').values=[['상품명','담보 행 수','약관 페이지','사업방법서 페이지','동일 약관 사본 수'],...per.map((v,d)=>[v.product,v.n,v.pages,business[d].pages.length,v.duplicates.length])];
summary.getRange('A10:B15').values=[['전체 담보 행 수',650],['보험료 납입면제 담보',18],['상품 폴더 수',8],['원본 PDF 수',16],['중복 제외 PDF 수',8],['중복 제외 약관 페이지',15398]];
const method=[
 ['처리 기준','담보 하나를 한 행으로 저장. 동일 파일은 SHA-256으로 비교하여 중복 행을 생성하지 않음.'],
 ['담보명 구분','같은 담보명의 혼동을 줄이기 위해 담보명 뒤에 주계약 유형 또는 특약명을 표시.'],
 ['보장금액','표에 기재된 보험가입금액 기준·금액·계산식을 보존. 예시금액을 모든 계약의 확정 지급액으로 해석하지 않음.'],
 ['보장조건','지급사유, 지급기준표 주석 및 본문상 제외사항을 추출. 원문의 줄바꿈에 따른 일부 띄어쓰기 차이가 있을 수 있음.'],
 ['생성·수정일시','시간대를 보존한 날짜·시각 문자열(+09:00). Excel에는 TIMESTAMPTZ 형식이 없어 텍스트로 저장.'],
 ['검증 범위','16개 파일 대조, 전체 약관 텍스트 검색, 지급기준표 439개와 납입면제 18개 확인, 필수값·중복·페이지 연결 검사 및 대표 원문 시각 대조.'],
 ['긴 조건 읽기','긴 보장조건은 셀을 선택하여 수식 입력줄에서 전체 내용을 확인. Excel의 행 높이 제한 때문에 긴 셀은 화면에 일부만 보일 수 있음.'],
 ['계약별 확인','실제 가입 특약·가입금액·심사유형은 개별 보험증권 기준. 공시 약관에 수록된 특약 전체를 정리함.'],
 ['출처 확인','출처·검토 시트의 id가 담보데이터 id와 연결됨. 페이지는 PDF의 실제 페이지 번호.']
];
summary.getRange('A18:A26').values=method.map(([a,b])=>[a+' — '+b]);
base(summary,'A1:E26',[68,15,20,22,22]);summary.getRange('A4:E4').format={fill:'#153957',font:{name:'Malgun Gothic',size:10,bold:true,color:'#FFFFFF'},rowHeight:28};summary.getRange('A5:E8').format.rowHeight=42;summary.getRange('A10:B15').format.rowHeight=26;
for(let i=0;i<method.length;i++)summary.getRange(`A${18+i}:E${18+i}`).format.rowHeight=Math.max(45,Math.ceil((method[i][0]+method[i][1]).length/45)*15+10);
summary.getRange('B5:E8').setNumberFormat('0');summary.getRange('B10:B15').setNumberFormat('0');
const sh=['id','상품명','주계약·특약','심사유형','출처 파일','PDF 페이지','동일 파일 출처','검토사항'];
const sr=rec.map(r=>[r.id,r.product,r.section,r.section.includes('간편심사형')?'간편심사형':r.section.includes('일반심사형')?'일반심사형':'해당 문서 기준',counts[r.doc].file,r.page===r.page_end?String(r.page):`${r.page}–${r.page_end}`,per[r.doc].duplicates.join('\n'),r.name.includes('납입면제')?'지급기준표 없이 본문 납입면제 조항에서 추출':r.name.includes('사망 시 지급금')?'계약소멸 시 계약자 지급금; 지급기준표 주석에서 추출':r.page_end>r.page?'페이지를 넘기는 지급기준표를 연결하여 추출':'지급기준표와 본문을 연결하여 추출']);
source.getRange(`A1:H${sr.length+1}`).values=[sh,...sr];base(source,`A1:H${sr.length+1}`,[8,43,65,18,100,16,100,55]);source.getRange('A1:H1').format={fill:'#49657A',font:{name:'Malgun Gothic',size:10,bold:true,color:'#FFFFFF'},rowHeight:30};source.getRange(`A2:H${sr.length+1}`).format.rowHeight=84;source.tables.add(`A1:H${sr.length+1}`,true,'SourceDetails');source.freezePanes.freezeRows(1);
wb.recalculate();
console.log((await wb.inspect({kind:'table',range:'담보데이터!A1:I3',tableMaxRows:3,tableMaxCols:9,tableMaxCellChars:80,maxChars:2500})).ndjson);
for(const [s,range,name] of [['담보데이터','A1:D3','data'],['처리현황','A2:E26','summary'],['출처·검토','A1:D4','sources'],['담보데이터','D35:G36','details'],['담보데이터','H1:I3','times']]){
 const blob=await wb.render({sheetName:s,range,scale:1.5,format:'png'});await fs.writeFile(`work/${name}_preview.png`,new Uint8Array(await blob.arrayBuffer()));
}
await fs.mkdir('outputs',{recursive:true});const out=await SpreadsheetFile.exportXlsx(wb);await out.save('outputs/ABL생명_2507_담보분석.xlsx');
console.log('SAVED',data.length);
