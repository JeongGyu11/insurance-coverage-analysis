import fs from 'node:fs/promises';
import {getDocument} from 'pdfjs-dist/legacy/build/pdf.mjs';
const inv=JSON.parse(await fs.readFile('work/kb/inventory.json','utf8')),seen=new Set(),manifest=[];
for(const f of inv){
 if(!f.path.endsWith('.pdf')||seen.has(f.hash))continue;seen.add(f.hash);
 const key=`doc${manifest.length}`,pdf=await getDocument({data:new Uint8Array(await fs.readFile(f.path)),cMapUrl:'C:/Users/FAS/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/pdfjs-dist/cmaps/',cMapPacked:true}).promise,pages=[];
 for(let n=1;n<=pdf.numPages;n++){
  const p=await pdf.getPage(n),tc=await p.getTextContent(),rows=new Map(),dupes=new Set();
  for(const it of tc.items){if(!it.str)continue;const [x,y]=[it.transform[4],it.transform[5]],k=it.str+'|'+Math.round(x*10)+'|'+Math.round(y*10);if(dupes.has(k))continue;dupes.add(k);const yy=Math.round(y/2)*2;if(!rows.has(yy))rows.set(yy,[]);rows.get(yy).push({x,t:it.str});}
  pages.push([...rows].sort((a,b)=>b[0]-a[0]).map(([y,l])=>l.sort((a,b)=>a.x-b.x).map(a=>a.t).join(' ')).join('\n'));p.cleanup();
 }
 await fs.writeFile(`work/kb/${key}.json`,JSON.stringify(pages));await fs.writeFile(`work/kb/${key}.txt`,pages.map((t,i)=>`=== PAGE ${i+1} ===\n${t}`).join('\n'));
 manifest.push({...f,key,pages:pdf.numPages,duplicate_paths:inv.filter(i=>i.hash===f.hash&&i.path!==f.path).map(i=>i.path)});console.log(key,f.kind,pdf.numPages);await pdf.destroy();
}
await fs.writeFile('work/kb/manifest.json',JSON.stringify(manifest));

