import fs from 'node:fs/promises';
import {getDocument} from 'pdfjs-dist/legacy/build/pdf.mjs';
const root='C:/Users/FAS/Desktop/데이터분석/AIG손해보험_2507';
const dirs=(await fs.readdir(root)).sort();const manifest=[];
for(let d=0;d<dirs.length;d++){
 const file=`${root}/${dirs[d]}/약관.pdf`;
 const pdf=await getDocument({data:new Uint8Array(await fs.readFile(file)),cMapUrl:'C:/Users/FAS/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/pdfjs-dist/cmaps/',cMapPacked:true}).promise;
 const pages=[];const flow=[];
 for(let n=1;n<=pdf.numPages;n++){
  const p=await pdf.getPage(n),tc=await p.getTextContent(),width=p.view[2];let cols=[new Map(),new Map()],seen=new Set();
  for(const it of tc.items){if(!it.str)continue;const [x,y]=[it.transform[4],it.transform[5]],k=it.str+'|'+Math.round(x*10)+'|'+Math.round(y*10);if(seen.has(k))continue;seen.add(k);const col=x<width/2?0:1,yy=Math.round(y/2)*2;if(!cols[col].has(yy))cols[col].set(yy,[]);cols[col].get(yy).push({x,t:it.str});}
  const texts=cols.map(c=>[...c].sort((a,b)=>b[0]-a[0]).map(([y,l])=>l.sort((a,b)=>a.x-b.x).map(a=>a.t).join(' ')).join('\n'));
  pages.push(texts);for(let c=0;c<2;c++)flow.push({page:n,col:c,text:texts[c]});p.cleanup();
 }
 await fs.writeFile(`work/aig/policy${d}.json`,JSON.stringify({path:file,pages,flow}));
 await fs.writeFile(`work/aig/policy${d}.txt`,flow.map(f=>`=== PAGE ${f.page} COL ${f.col} ===\n${f.text}`).join('\n'));
 console.log('policy',d,pdf.numPages);await pdf.destroy();
}
