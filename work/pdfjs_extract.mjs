import fs from 'node:fs/promises';
import {getDocument} from 'pdfjs-dist/legacy/build/pdf.mjs';
const counts=JSON.parse(await fs.readFile('work/counts.json','utf8'));
await fs.mkdir('work/fast',{recursive:true});
for(let d=0;d<counts.length;d++){
 const pdf=await getDocument({data:new Uint8Array(await fs.readFile(counts[d].file)),useSystemFonts:true}).promise;
 const pages=[];
 for(let n=1;n<=pdf.numPages;n++){
  const page=await pdf.getPage(n),tc=await page.getTextContent();
  const rows=new Map(),seen=new Set();
  for(const it of tc.items){if(!it.str)continue;let [x,y]=[it.transform[4],it.transform[5]],k=it.str+'|'+Math.round(x*10)+'|'+Math.round(y*10);if(seen.has(k))continue;seen.add(k);let ky=Math.round(y/2)*2;if(!rows.has(ky))rows.set(ky,[]);rows.get(ky).push({x,s:it.str});}
  pages.push([...rows].sort((a,b)=>b[0]-a[0]).map(([y,it])=>it.sort((a,b)=>a.x-b.x).map(a=>a.s).join(' ')).join('\n'));
  page.cleanup();
  if(n%250===0)console.log(d,n);
 }
 await fs.writeFile(`work/fast/p${d}.json`,JSON.stringify(pages));
 await fs.writeFile(`work/fast/p${d}.txt`,pages.map((t,i)=>`\n=== PDF PAGE ${i+1} ===\n${t}`).join('\n'));
 console.log('DONE',d,pages.length);await pdf.destroy();
}
