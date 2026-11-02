// Layout check: opens the running dev site at many screen sizes, scrolls every chapter and reports anything that must be on screen but is not
// (a figure cut off by the edge, the karate board off to the side, copy under the Journey buttons, a diagram over his face ...).
//
//   npm run dev                          (in one terminal; the site must be on http://localhost:5175 or pass --url)
//   node tools/layout-check.mjs          all devices
//   node tools/layout-check.mjs --only "iPad Mini,Galaxy A55" --chapters karate,keyboard
//   node tools/layout-check.mjs --shots  also save a screenshot of every chapter on every device (tools/out/shots)
//
// Writes tools/out/layout-report.json and tools/out/layout-report.md; exits 1 if anything failed.
import { chromium } from 'playwright-core'
import { existsSync, mkdirSync, readdirSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'

const arg = (name, fallback) => {
  const i = process.argv.indexOf('--' + name)
  return i < 0 ? fallback : process.argv[i + 1] && !process.argv[i + 1].startsWith('--') ? process.argv[i + 1] : true
}
const URL_ = arg('url', 'http://localhost:5175/')
const ONLY = arg('only', '') ? String(arg('only')).split(',').map((s) => s.trim().toLowerCase()) : null
const CHAPTERS = arg('chapters', '') ? String(arg('chapters')).split(',').map((s) => s.trim()) : null
const SHOTS = !!arg('shots', false)
const TAG = arg('tag', '')
const POINTS = [0.08, 0.22, 0.36, 0.5, 0.64, 0.78, 0.92] // how far through each chapter's pinned scroll we look

// css pixels; touch = phone-like input
const DEVICES = [
  { name: 'Galaxy A55', w: 412, h: 915, dpr: 2.6, touch: true },
  { name: 'iPhone SE', w: 375, h: 667, dpr: 2, touch: true },
  { name: 'iPhone 12 mini', w: 360, h: 780, dpr: 3, touch: true },
  { name: 'iPhone 14', w: 390, h: 844, dpr: 3, touch: true },
  { name: 'iPhone 14 Pro Max', w: 430, h: 932, dpr: 3, touch: true },
  { name: 'Pixel 5', w: 393, h: 851, dpr: 2.75, touch: true },
  { name: 'Galaxy S8', w: 360, h: 740, dpr: 4, touch: true },
  { name: 'Galaxy Fold folded', w: 280, h: 653, dpr: 3, touch: true },
  { name: 'Surface Duo', w: 540, h: 720, dpr: 2.5, touch: true },
  { name: 'iPad Mini', w: 768, h: 1024, dpr: 2, touch: true },
  { name: 'iPad Air', w: 820, h: 1180, dpr: 2, touch: true },
  { name: 'iPad Pro 11', w: 834, h: 1194, dpr: 2, touch: true },
  { name: 'iPad Pro 12.9', w: 1024, h: 1366, dpr: 2, touch: true },
  { name: 'Phone landscape (A55)', w: 915, h: 412, dpr: 2.6, touch: true },
  { name: 'Phone landscape (iPhone 14)', w: 844, h: 390, dpr: 3, touch: true },
  { name: 'Phone landscape + address bar (A55)', w: 915, h: 355, dpr: 2.6, touch: true },
  { name: 'Phone landscape + address bar (iPhone 14)', w: 844, h: 330, dpr: 3, touch: true },
  { name: 'Phone landscape + address bar (S8)', w: 740, h: 290, dpr: 4, touch: true },
  { name: 'Tablet landscape (iPad Mini)', w: 1024, h: 768, dpr: 2, touch: true },
  { name: 'Laptop 1440x900', w: 1440, h: 900, dpr: 1, touch: false },
  { name: 'Desktop 1920x1080', w: 1920, h: 1080, dpr: 1, touch: false },
]

const chromePath = () => {
  if (process.env.CHROME_PATH) return process.env.CHROME_PATH
  const root = join(process.env.LOCALAPPDATA ?? '', 'ms-playwright')
  if (!existsSync(root)) return undefined
  for (const d of readdirSync(root).filter((n) => n.startsWith('chromium-')).sort().reverse()) {
    for (const sub of readdirSync(join(root, d))) {
      const p = join(root, d, sub, 'chrome.exe')
      if (existsSync(p)) return p
    }
  }
  return undefined
}

// runs inside the page: measures one chapter at the current scroll position and returns the problems it sees
const measure = (mid) => {
  const vw = innerWidth
  const vh = innerHeight
  const TOL = 3
  const out = []
  const portrait = matchMedia('(max-aspect-ratio: 9/10), (max-width: 760px) and (min-height: 561px)').matches
  const vis = (el) => {
    for (let n = el; n && n !== document.body; n = n.parentElement) {
      const cs = getComputedStyle(n)
      if (cs.display === 'none' || cs.visibility === 'hidden' || Number(cs.opacity) < 0.08) return false
    }
    return true
  }
  const r = (el) => el.getBoundingClientRect()
  const sec = [...document.querySelectorAll('section.chapter--stage')].find((s) => {
    const b = s.getBoundingClientRect()
    return b.top <= vh * 0.5 && b.bottom > vh * 0.5
  })
  if (!sec) return { id: null, problems: [] }
  const id = sec.id
  const pin = sec.querySelector('.chapter__pin')
  const outside = (b) => ({ left: Math.round(b.left), right: Math.round(b.right), top: Math.round(b.top), bottom: Math.round(b.bottom) })

  // the star figure (his body) must be fully inside the screen sideways and not clipped at the top
  const stars = [...sec.querySelectorAll('.cs__item--star')].filter((e) => vis(e) && !e.dataset.move && (portrait || e.dataset.travels === undefined))
  const starImgs = stars.flatMap((s) => [...s.querySelectorAll('img.cs__img')].filter((i) => vis(i) && Number(getComputedStyle(i).opacity) > 0.5))
  for (const img of starImgs) {
    const b = r(img)
    if (b.width < 2) continue
    if (b.left >= -TOL && b.left < vw * 0.012) out.push({ kind: 'figure-touches-left-edge', box: outside(b) })
    if (b.right <= vw + TOL && b.right > vw * 0.988) out.push({ kind: 'figure-touches-right-edge', box: outside(b) })
    if (b.left < -TOL) out.push({ kind: 'figure-cut-left', by: Math.round(-b.left), box: outside(b) })
    if (b.right > vw + TOL) out.push({ kind: 'figure-cut-right', by: Math.round(b.right - vw), box: outside(b) })
    if (b.top < -TOL) out.push({ kind: 'figure-cut-top', by: Math.round(-b.top), box: outside(b) })
  }
  // every other item that is shown (props, second pose) must at least start inside
  for (const it of sec.querySelectorAll('.cs__item:not(.cs__item--star)')) {
    if (!portrait || !vis(it) || it.dataset.move || false) continue
    for (const img of it.querySelectorAll('img.cs__img')) {
      if (!vis(img) || Number(getComputedStyle(img).opacity) < 0.5) continue
      const b = r(img)
      if (b.width < 2) continue
      if (b.left < -14 || b.right > vw + 14) out.push({ kind: 'prop-off-screen', box: outside(b) })
    }
  }
  // props that pop in (the karate board, hop objects); the wide layout is the locked desktop look and is not judged here
  for (const ex of sec.querySelectorAll('.cs__extra')) {
    if (!vis(ex) || !portrait) continue
    const img = ex.querySelector('img') ?? ex
    const b = r(img)
    if (b.width < 2) continue
    if (b.left < -14 || b.right > vw + 14 || b.bottom > vh + TOL) out.push({ kind: 'extra-off-screen', box: outside(b) })
  }
  // cats in the scene
  for (const c of sec.querySelectorAll('.cs__cat')) {
    const b = r(c)
    if (b.width > 2 && (b.left < -TOL || b.right > vw + TOL || b.top < 0 || b.bottom > vh + TOL)) out.push({ kind: 'cat-off-screen', box: outside(b) })
  }
  // the copy block and the Journey buttons
  const text = sec.querySelector('.chapter__text')
  const jw = document.querySelector('.journey-wrap')
  if (text && vis(text)) {
    const b = r(text)
    if (b.left < -TOL || b.right > vw + TOL) out.push({ kind: 'copy-off-screen-sideways', box: outside(b) })
    if (b.bottom > vh + TOL) out.push({ kind: 'copy-below-screen', by: Math.round(b.bottom - vh) })
    if (jw) {
      const j = r(jw)
      if (b.bottom > j.top + 2 && b.top < j.bottom && b.left < j.right && b.right > j.left) out.push({ kind: 'copy-under-journey-buttons', by: Math.round(b.bottom - j.top) })
    }
    // copy must not sit on his face: the star's top 40 per cent
    for (const img of starImgs) {
      const f = r(img)
      const headBottom = f.top + f.height * 0.4
      if (b.top < headBottom && b.bottom > f.top && b.right > f.left && b.left < f.right) out.push({ kind: 'copy-over-face', by: Math.round(headBottom - b.top) })
    }
  }
  // the progress line
  const tr = sec.querySelector('.cs__trace')
  if (tr && vis(tr)) {
    const b = r(tr)
    if (b.bottom > vh + TOL || b.top < 0) out.push({ kind: 'progress-line-off-screen', box: outside(b) })
  }
  // diagrams over his head: any drawn piece of an overlay graphic (a line, a cell, a label, the terminal) touching his head, which is
  // taken as the top third of the figure and its middle 56 per cent
  for (const ov of sec.querySelectorAll('.cs__over')) {
    if (ov.classList.contains('cs__over--in')) continue
    const parts = [...ov.querySelectorAll('svg path, svg rect, svg circle, svg line, svg text, .term, .ov-eq span')].filter(vis)
    for (const part of parts) {
      const b = r(part)
      if (b.width < 2 && b.height < 2) continue
      if (b.left < -TOL || b.right > vw + TOL) out.push({ kind: 'diagram-off-screen', box: outside(b) })
      for (const img of starImgs) {
        const f = r(img)
        const head = { left: f.left + f.width * 0.22, right: f.right - f.width * 0.22, top: f.top, bottom: f.top + f.height * 0.33 }
        const w = Math.min(b.right, head.right) - Math.max(b.left, head.left)
        const h = Math.min(b.bottom, head.bottom) - Math.max(b.top, head.top)
        if (w > 8 && h > 8) {
          out.push({ kind: 'diagram-over-face', box: outside(b) })
          break
        }
      }
    }
  }
  return { id, problems: out, pin: pin ? outside(r(pin)) : null }
}

// acts: every cat on an act card must be reachable: on screen and clear of the Journey buttons at some point while the card is pinned
const measureAct = (idx) => {
  const vw = innerWidth
  const vh = innerHeight
  const out = []
  const a = document.querySelectorAll('.act')[idx]
  const jw = document.querySelector('.journey-wrap')
  const j = jw?.getBoundingClientRect()
  for (const c of a.querySelectorAll('.cat')) {
    const cb = c.getBoundingClientRect()
    if (cb.width < 2) continue
    const probs = []
    if (cb.left < 0 || cb.right > vw) probs.push('act-cat-off-screen-sideways')
    if (cb.bottom > vh || cb.top < 0) probs.push('act-cat-off-screen-vertically')
    if (j && cb.bottom > j.top && cb.top < j.bottom && cb.left < j.right && cb.right > j.left) probs.push('act-cat-under-journey-buttons')
    out.push({ id: a.id || 'act' + idx, probs })
  }
  return out
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms))

const main = async () => {
  const outDir = fileURLToPath(new URL('./out/', import.meta.url))
  mkdirSync(join(outDir, 'shots'), { recursive: true })
  const browser = await chromium.launch({ executablePath: chromePath(), headless: true })
  const report = []
  const devices = DEVICES.filter((d) => !ONLY || ONLY.some((o) => d.name.toLowerCase().includes(o)))

  for (const dev of devices) {
    const ctx = await browser.newContext({
      viewport: { width: dev.w, height: dev.h },
      deviceScaleFactor: Math.min(dev.dpr, 2),
      hasTouch: dev.touch,
      isMobile: dev.touch,
      userAgent: dev.touch ? 'Mozilla/5.0 (Linux; Android 14; SM-A556B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Mobile Safari/537.36' : undefined,
    })
    const page = await ctx.newPage()
    await page.goto(URL_ + '?layoutcheck', { waitUntil: 'domcontentloaded' })
    await page.waitForFunction(() => !!window.lenis && document.querySelectorAll('section.chapter--stage').length > 0, null, { timeout: 60000 })
    await page.evaluate(() => {
      document.getElementById('boot')?.remove()
      document.documentElement.classList.remove('booting')
    })
    await sleep(800)
    const chapters = await page.evaluate(() =>
      [...document.querySelectorAll('section.chapter--stage')].map((s) => ({ id: s.id, top: s.getBoundingClientRect().top + scrollY, h: s.offsetHeight })),
    )
    const found = []
    for (const ch of chapters) {
      if (CHAPTERS && !CHAPTERS.includes(ch.id)) continue
      for (const p of POINTS) {
        const y = ch.top + p * Math.max(0, ch.h - dev.h)
        await page.evaluate((yy) => window.lenis.scrollTo(yy, { immediate: true, force: true }), y)
        await sleep(450)
        const m = await page.evaluate(measure, Math.abs(p - 0.5) < 0.05)
        if (m.id !== ch.id) continue
        for (const pr of m.problems) found.push({ chapter: ch.id, at: p, ...pr })
        if (SHOTS && p === POINTS[3]) await page.screenshot({ path: join(outDir, 'shots', `${dev.name.replace(/[^a-z0-9]+/gi, '_')}__${ch.id}.png`) })
      }
    }
    // act cards: look at a few positions while the card is on screen; a cat is fine if it is reachable at one of them
    const acts = await page.evaluate(() => [...document.querySelectorAll('.act')].map((a) => ({ top: a.getBoundingClientRect().top + scrollY, h: a.offsetHeight })))
    for (let i = 0; i < acts.length; i++) {
      const a = acts[i]
      const best = new Map()
      for (const f of [0.2, 0.4, 0.6, 0.8, 1.0]) {
        await page.evaluate((yy) => window.lenis.scrollTo(yy, { immediate: true, force: true }), a.top + (a.h - dev.h) * f)
        await sleep(350)
        const cats = await page.evaluate(measureAct, i)
        cats.forEach((c, k) => {
          const prev = best.get(k)
          if (!prev || c.probs.length < prev.probs.length) best.set(k, c)
        })
      }
      for (const c of best.values()) for (const pr of c.probs) found.push({ chapter: 'act:' + c.id, at: 0.5, kind: pr })
    }
    // collapse repeats: same chapter + kind
    const key = new Map()
    for (const f of found) {
      const k = f.chapter + '|' + f.kind
      if (!key.has(k)) key.set(k, { ...f, count: 1, points: [f.at] })
      else {
        const e = key.get(k)
        e.count++
        e.points.push(f.at)
      }
    }
    const problems = [...key.values()]
    report.push({ device: dev.name, size: `${dev.w}x${dev.h}`, problems })
    console.log(`${problems.length ? 'FAIL' : 'ok  '}  ${dev.name} (${dev.w}x${dev.h}): ${problems.length} problem kinds`)
    await ctx.close()
  }
  await browser.close()

  writeFileSync(join(outDir, `layout-report${TAG}.json`), JSON.stringify(report, null, 2))
  const lines = ['# Layout check', '']
  let total = 0
  for (const d of report) {
    total += d.problems.length
    lines.push(`## ${d.device} (${d.size}): ${d.problems.length ? d.problems.length + ' problems' : 'ok'}`)
    for (const p of d.problems) lines.push(`- **${p.chapter}**: ${p.kind}${p.by ? ' by ' + p.by + 'px' : ''} (seen ${p.count}x)`)
    lines.push('')
  }
  writeFileSync(join(outDir, `layout-report${TAG}.md`), lines.join('\n'))
  console.log(`\n${total} problem kinds in total. Report: tools/out/layout-report.md`)
  process.exit(total ? 1 : 0)
}
main().catch((e) => {
  console.error(e)
  process.exit(2)
})
