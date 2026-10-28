const {chromium}=require('playwright');const path=require('path');const fs=require('fs');
(async()=>{const [n,out]=[process.argv[2],process.argv[3]];fs.mkdirSync(out,{recursive:true});
const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+path.resolve('reel.html')+'?r='+n);await p.evaluate(()=>document.fonts.ready);
const dur=await p.evaluate(()=>window.DUR);const N=dur*30;
for(let f=0;f<N;f++){await p.evaluate(t=>render(t),f/30);await p.screenshot({path:`${out}/f${String(f).padStart(4,'0')}.png`});}
await b.close();})();
