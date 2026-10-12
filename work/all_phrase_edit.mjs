import fs from 'node:fs/promises';
import {SpreadsheetFile,FileBlob} from '@oai/artifact-tool';
const results=JSON.parse(await fs.readFile('work/all_phrase/results.json','utf8'));
const preview=process.argv.includes('--preview');
for(const x of results.filter(x=>x.changes.length)){
 const w=await SpreadsheetFile.importXlsx(await FileBlob.load(x.path));
 const s=w.worksheets.getItem('담보데이터'),row=x.changes[0].cell.slice(1);
 if(!preview){
  const stamp=new Date(Date.now()+9*3600000).toISOString().slice(0,19).replace('T',' ')+'+09:00';
  for(const v of x.changes){s.getRange(v.cell).values=[[v.new]];s.getRange('I'+v.cell.slice(1)).values=[[stamp]];}
  w.recalculate();
  await (await SpreadsheetFile.exportXlsx(w)).save('outputs/01a10ed0-eb0e-7720-80fe-23aace7c950b/'+x.name+'_2507_담보분석.xlsx');
 }
 const b=await w.render({sheetName:'담보데이터',range:'E'+row+':G'+row,scale:0.8,format:'png'});
 await fs.writeFile('work/all_phrase/'+x.name+'_'+(preview?'before':'after')+'.png',new Uint8Array(await b.arrayBuffer()));
 console.log(x.name,preview?'PREVIEW':x.changes.length);
}

