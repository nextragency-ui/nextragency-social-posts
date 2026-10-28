const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1200, height: 1500 }, deviceScaleFactor: 1 });
  await page.goto('file://' + path.resolve(process.argv[2]));
  await page.evaluate(() => document.fonts.ready);
  const outDir = process.argv[3];
  for (let i = 1; i <= 7; i++) {
    const el = await page.$('#s' + i);
    await el.screenshot({ path: `${outDir}/slide-${i}.png` });
  }
  // Overlap check: headline/content vs brand bar and visuals
  const report = await page.evaluate(() => {
    const out = [];
    document.querySelectorAll('.slide').forEach(s => {
      const sr = s.getBoundingClientRect();
      const c = s.querySelector('.content');
      const cr = c.getBoundingClientRect();
      const kids = [...c.querySelectorAll('h1,h2,.body,.card,.row,.panel,.step')];
      let maxBottom = 0;
      kids.forEach(k => { maxBottom = Math.max(maxBottom, k.getBoundingClientRect().bottom - sr.top); });
      out.push({ id: s.id, contentBottom: Math.round(maxBottom), limit: 1150 });
    });
    return out;
  });
  console.log(JSON.stringify(report));
  console.log('font check:', await page.evaluate(() => document.fonts.check('900 40px Inter')));
  await browser.close();
})();
