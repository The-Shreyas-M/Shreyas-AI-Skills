# Deploy, SEO, speed (what was done, in order, and what to copy)

## Repo hygiene before the first push

1. Make a **bundle backup** of the old history (`git bundle create ../backup.bundle --all`) and keep the old folder untouched.
2. Remove raw working files from every commit with `git filter-repo --invert-paths --path <raw-folders>` (here ~250 MB of raw models, test renders and personal photos became ~28 MB). Keep one editable source (the master `.blend`) as a single copy.
3. Keep the repo **private**; Cloudflare Pages can deploy from a private repo. Put raw personal notes only in `ideas/` and never in code.
4. Branch plan: `main` = production (auto-deploys); a frozen reference branch for the approved look; a work branch for risky work that gets its own preview address.

## Cloudflare Pages

- Create: Workers & Pages, Pages, import from Git; authorise the GitHub app on **only this repo**.
- Build command `npm run build`, output `dist`, env `NODE_VERSION=22` (recent Vite needs it), production branch `main`.
- Project name gives `<name>.pages.dev`. A custom domain is optional (parked here: a free-domain service was rejected for reputation).
- **KV counter**: create a KV namespace, add a binding named exactly as the function expects (`LIKES`), then push an empty commit (bindings apply on the next deploy). Reset any test counts in the KV dashboard.
- Rollback: Deployments, pick an old one, Rollback.
- Never type or store passwords/tokens in the repo; per-command tokens for pushes (`GH_TOKEN=$(gh auth token --user <login>)`), the repo records which account owns it.

## Headers (`public/_headers`)

- `/assets/*` immutable for a year (hashed file names); fonts/images/models a day with stale-while-revalidate; **`/`, `/index.html` and `/asset-manifest.json` = `no-cache`** so nobody is ever shown an old version (a normal browser held the old page; incognito did not).
- Read the **deployed CSS** after a build: a minifier dropped `backdrop-filter` when `-webkit-backdrop-filter` shared its rule.

## SEO and sharing

Title and description, canonical, `og:*` and Twitter tags with an **absolute** share image (1200x630), apple-touch icon, favicon (a Gemini-made avatar head as ico/png), sitemap.xml, robots.txt, JSON-LD (Person/WebSite), a custom 404, a `<noscript>` line, Search Console: verify (HTML file in `public/`), submit the sitemap (first fetch often says "Couldn't fetch": normal), "Request indexing" (may say "something went wrong": retry later). Put the link on profiles (LinkedIn, GitHub, YouTube, Instagram) to build trust.

## Speed

- Self-host fonts (`@fontsource/*`), preload the avatar GLB in the HTML, vendor chunks (`three`, `gsap+lenis`, `react`), far-chapter freezing, a still gradient instead of a CSS mask on moving layers, a lower pixel ratio on phones for the 3D canvas.
- **Loading screen** (inline in `index.html`, works before React): face, title, a segmented bar, cycling lines about the owner (time-based, not progress-based), a compositor-animated pre-glow so it never looks frozen while scripts start. Real progress = bytes of every picture and the model listed in a generated `asset-manifest.json` (`scripts/make-asset-manifest.mjs`, run in `predev`/`prebuild`); fetch them with 8 in flight; the bar is 88% downloads, the rest waits for the avatar to be **stably** drawn; 20 s safety timeout; a compact version for short landscape screens.
- Measure on a real phone: an `?fps` overlay (fps, worst frame, current section, 3D status) shows which chapters stutter. Sitting still at 60 and dipping only during fast flicks is fine.

## The Mixamo / Blender notes

Record every Mixamo animation (name, file name, GLB clip name), the rig settings ("with skin") and the Blender commands in `MIXAMO.md` as you go.
