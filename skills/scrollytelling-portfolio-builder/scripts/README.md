# Scripts

Copied from the "I Am Shreyas" build. They are **examples to adapt**, not a package: selectors and folder names are from that project.

| File | What | Adapt |
|---|---|---|
| `layout-check.mjs` | Opens the running dev site in headless Chromium at 21 screen sizes, scrolls every chapter, flags cut-off figures, props, copy under buttons, copy/diagrams over the face; `--shots`, `--only`, `--chapters`, `--tag`. Needs `playwright-core` (`npm i -D playwright-core`) and an installed Chromium (the script looks in `%LOCALAPPDATA%/ms-playwright` or `CHROME_PATH`). | selectors: `section.chapter--stage`, `.cs__item--star`, `.cs__extra`, `.chapter__text`, `.journey-wrap`, `.cs__trace`; the dev server exposes `window.lenis` and honours `?layoutcheck` |
| `desktop-diff.mjs` | Screenshots two servers (reference vs branch) at desktop sizes and scroll points; pass `A` or `B` as the 4th argument to shoot only one. Compare in Python with the images resized 8x (box filter) to ignore film grain. | the chapter selector and `window.lenis` |
| `page-shots.mjs` | Hero, act card, a long chapter and the ending on five sizes. | positions |
| `make-asset-manifest.mjs` | Writes `public/asset-manifest.json` (every image/model with its size) for the loading screen's byte progress. Hook into `predev` and `prebuild`; gitignore the output. | folders |
| `key_cutouts.py` | Green-screen keying of generated images into trimmed WebP with alpha; strips become pose frames. Needs Pillow, numpy, scipy. | the file-name prefixes and output folders |
| `prep_bgs.py` | Backgrounds: remove the corner watermark, resize to 1920 wide, WebP. | sizes |

The dev server must run first (`npm run dev`, port in the scripts). On Windows run the three batches of `layout-check` in the background and wait for the report files; a stopped dev server makes every batch fail with `ERR_CONNECTION_REFUSED` (check it first).
