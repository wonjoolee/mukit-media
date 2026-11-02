// 사용: node pipeline/render.js <kit.html 경로> <출력폴더>
// kit.html 안의 .card 요소(순서대로, 최대 10장)를 01.png, 02.png ... (1080x1350)로 저장
const {chromium}=require('playwright');const path=require('path');const fs=require('fs');
const [html,out]=process.argv.slice(2);(async()=>{const b=await chromium.launch();
const p=await b.newPage({viewport:{width:3700,height:3200}});
await p.goto('file://'+path.resolve(html));await p.waitForLoadState('networkidle');await p.waitForTimeout(500);
fs.mkdirSync(out,{recursive:true});const cards=await p.$$('.card');
for(let i=0;i<cards.length&&i<10;i++){await cards[i].screenshot({path:`${out}/${String(i+1).padStart(2,'0')}.png`});}
console.log('cards',cards.length);await b.close();})();
