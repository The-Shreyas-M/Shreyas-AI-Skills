// Lists every picture and model the site shows (public/media, public/models) with its size, so the loading screen can
// download them all before the site opens and its progress bar can be exact. Runs before `npm run dev` and `npm run build`.
import { readdirSync, statSync, writeFileSync } from 'node:fs'
import { join, extname, relative, sep } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = fileURLToPath(new URL('../public/', import.meta.url))
const OK = new Set(['.webp', '.png', '.jpg', '.jpeg', '.glb', '.svg'])
const files = []
const walk = (dir) => {
  for (const name of readdirSync(dir)) {
    const p = join(dir, name)
    if (statSync(p).isDirectory()) walk(p)
    else if (OK.has(extname(name).toLowerCase())) files.push({ u: '/' + relative(root, p).split(sep).join('/'), s: statSync(p).size })
  }
}
for (const d of ['models', 'media']) walk(join(root, d))
// the avatar model first (the page also preloads it), then the rest in a stable order
files.sort((a, b) => (b.u.endsWith('.glb') ? 1 : 0) - (a.u.endsWith('.glb') ? 1 : 0) || a.u.localeCompare(b.u))
writeFileSync(join(root, 'asset-manifest.json'), JSON.stringify({ files }))
console.log(`asset manifest: ${files.length} files, ${(files.reduce((n, f) => n + f.s, 0) / 1048576).toFixed(1)} MB`)
