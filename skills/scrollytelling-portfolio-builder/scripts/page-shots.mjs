// Screenshots of the hero, an act card, a long-copy chapter and the ending on a few screen sizes (tools/out/pages/).
//   node tools/page-shots.mjs [http://localhost:5175/]
import { chromium } from 'playwright-core'
import { existsSync, mkdirSync, readdirSync } from 'node:fs'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'
const URL_ = process.argv[2] ?? 'http://localhost:5175/'
const DEV = [
  ['A55', 412, 915, true], ['SE', 375, 667, true], ['iPadMini', 768, 1024, true], ['LandscapeA55', 915, 412, true], ['Fold', 280, 653, true],
]
const sleep = (ms) => new Promise((r) => setTimeout(r, ms))
const root = join(process.env.LOCALAPPDATA ?? '', 'ms-playwright')
let exe
for (const d of readdirSync(root).filter((n) => n.startsWith('chromium-'))) for (const s of readdirSync(join(root, d))) { const p = join(root, d, s, 'chrome.exe'); if (existsSync(p)) exe = p }
const out = fileURLToPath(new URL('./out/pages/', import.meta.url))
mkdirSync(out, { recursive: true })
const b = await chromium.launch({ executablePath: exe })
for (const [name, w, h, touch] of DEV) {
  const ctx = await b.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: 1, hasTouch: touch, isMobile: touch })
  const page = await ctx.newPage()
  await page.goto(URL_ + '?layoutcheck', { waitUntil: 'domcontentloaded' })
  await page.waitForFunction(() => !!window.lenis && document.querySelectorAll('section.chapter--stage').length > 0, null, { timeout: 90000 })
  await page.evaluate(() => { document.getElementById('boot')?.remove(); document.documentElement.classList.remove('booting') })
  await sleep(1500)
  const shot = async (label, y) => {
    await page.evaluate((yy) => window.lenis.scrollTo(yy, { immediate: true, force: true }), y)
    await sleep(900)
    await page.screenshot({ path: join(out, `${name}__${label}.png`) })
  }
  const pos = await page.evaluate(() => {
    const act = document.querySelector('.act')
    const words = document.querySelector('#words')
    return { act: act.getBoundingClientRect().top + scrollY, actH: act.offsetHeight, words: words.getBoundingClientRect().top + scrollY, wordsH: words.offsetHeight, max: document.documentElement.scrollHeight - innerHeight }
  })
  await shot('1_hero', 0)
  await shot('2_hero_wardrobe', h * 1.6)
  await shot('3_act', pos.act + (pos.actH - h) * 0.9)
  await shot('4_words', pos.words + (pos.wordsH - h) * 0.5)
  await shot('5_end', pos.max)
  await ctx.close()
  console.log(name, 'done')
}
await b.close()
