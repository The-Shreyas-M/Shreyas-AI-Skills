// Desktop look check: opens two copies of the site (the live desktop code and the current branch) at desktop sizes, scrolls both to the same
// places in every chapter and saves a screenshot of each, so the two can be compared. The wide layout must come out the same.
//
//   node tools/desktop-diff.mjs http://localhost:5176/ http://localhost:5175/     (A = reference, B = branch under test)
//
// Writes tools/out/diff/A_<size>_<chapter>_<n>.png and B_...; compare with tools/desktop-diff.py
import { chromium } from 'playwright-core'
import { existsSync, mkdirSync, readdirSync } from 'node:fs'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'

const [A, B] = [process.argv[2], process.argv[3]]
const SIZES = [
  [1440, 900],
  [1920, 1080],
]
const POINTS = [0.12, 0.45, 0.8]
const sleep = (ms) => new Promise((r) => setTimeout(r, ms))

const chromePath = () => {
  const root = join(process.env.LOCALAPPDATA ?? '', 'ms-playwright')
  for (const d of readdirSync(root).filter((n) => n.startsWith('chromium-')).sort().reverse())
    for (const sub of readdirSync(join(root, d))) {
      const p = join(root, d, sub, 'chrome.exe')
      if (existsSync(p)) return p
    }
}

const out = fileURLToPath(new URL('./out/diff/', import.meta.url))
mkdirSync(out, { recursive: true })
const browser = await chromium.launch({ executablePath: chromePath(), headless: true })

for (const [tag, url] of [['A', A], ['B', B]].filter(([t]) => !process.argv[4] || process.argv[4] === t)) {
  for (const [w, h] of SIZES) {
    const ctx = await browser.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: 1 })
    const page = await ctx.newPage()
    await page.goto(url + '?layoutcheck', { waitUntil: 'domcontentloaded' })
    await page.waitForFunction(() => !!window.lenis && document.querySelectorAll('section.chapter--stage').length > 0, null, { timeout: 90000 })
    await page.evaluate(() => {
      document.getElementById('boot')?.remove()
      document.documentElement.classList.remove('booting')
      // freeze the random grain so screenshots can be compared
      const st = document.createElement('style')
      st.textContent = '.grain,.grain *{animation:none!important} *{caret-color:transparent!important}'
      document.head.appendChild(st)
    })
    await sleep(900)
    const chapters = await page.evaluate(() => [...document.querySelectorAll('section.chapter--stage')].map((s) => ({ id: s.id, top: s.getBoundingClientRect().top + scrollY, h: s.offsetHeight })))
    for (const ch of chapters) {
      let n = 0
      for (const p of POINTS) {
        await page.evaluate((y) => window.lenis.scrollTo(y, { immediate: true, force: true }), ch.top + p * Math.max(0, ch.h - h))
        await sleep(900)
        await page.screenshot({ path: join(out, `${tag}_${w}x${h}_${ch.id}_${n++}.png`) })
      }
    }
    await ctx.close()
    console.log(tag, w, h, 'done')
  }
}
await browser.close()
