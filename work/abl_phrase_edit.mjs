import fs from 'node:fs/promises';
import {SpreadsheetFile,FileBlob} from '@oai/artifact-tool';
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load('C:/Users/FAS/Desktop/데이터분석/ABL생명_2507_담보분석.xlsx'));
const sheet=wb.worksheets.getItem('담보데이터');
const preview=process.argv.includes('--preview');
if(!preview){
 const changes=JSON.parse(await fs.readFile('work/abl_phrase/changes.json','utf8'));
 const now=new Date();const korea=new Date(now.getTime()+9*3600000).toISOString().slice(0,19).replace('T',' ')+'+09:00';
 for(const x of changes){sheet.getRange(x.cell).values=[[x.new]];sheet.getRange('I'+x.cell.slice(1)).values=[[korea]];}
 wb.recalculate();
 await (await SpreadsheetFile.exportXlsx(wb)).save('outputs/01a10ed0-eb0e-7720-80fe-23aace7c950b/ABL생명_2507_담보분석.xlsx');
 console.log('CHANGED',changes.length,korea);
}
const b=await wb.render({sheetName:'담보데이터',range:'E36:G38',scale:0.8,format:'png'});
await fs.writeFile('work/abl_phrase/'+(preview?'before':'after')+'.png',new Uint8Array(await b.arrayBuffer()));

