# guide.json format

```json
{
  "out": "START-HERE.html",          // output file, relative to the json
  "title": "Start here",             // big heading
  "page_title": "START HERE: ...",   // browser tab (optional)
  "brand": "Blackedge Books",        // small caps text next to the logo
  "accent": "#ffd400",               // button/number colour
  "logo": "images/logo.jpg",         // or null
  "intro": "<p>html allowed</p>",
  "variables": {                     // become inputs in the sticky bar; {KEY} in any copy text is replaced on Sync
    "LINK": {"label": "Your Gumroad link", "default": "https://..."},
    "SITE": {"label": "Your site link",   "default": "https://..."}
  },
  "steps": [
    {"id": "g1", "title": "Gumroad: one-time setup", "minutes": 5, "blocks": [ ... ]}
  ]
}
```

## Block types

| type | fields | renders |
|---|---|---|
| `html` | `html` | raw html: use `<ol><li>` for the numbered what-to-click list, `<b>` for button names, `<code>` for file names |
| `copy` | `text`, `label` (button), `caption` (line above, optional) | dark box with a green copy button. `{LINK}` etc. are replaced live |
| `download` | `items: [{label, file, name}]` | yellow download buttons; `file` is embedded as base64, `name` is the saved file name |
| `image` | `file`, `alt` | embedded picture |
| `note` | `text` | small grey line |

Step ids must be unique (used for the saved tick state). Paths are relative to the json file.

## Suggested step list (the Blackedge launch, 7 steps)

1. Gumroad one-time setup (5 min): payout details, profile name, logo download.
2. Gumroad make the product (10 min): copy name, copy description, cover downloads, thumbnail, the ONE buyer file download.
3. Gumroad launch (5 min): refund 30 days, link ending, launch code, Publish, paste link in the top bar and Sync.
4. YouTube upload the main video: file path, title options (one copy button each), description with chapters, tags, audience setting, pinned comment.
5. Thumbnail with Gemini: site screenshots to download + a short prompt to copy; ask for 3 versions.
6. Post the Shorts: per Short the file name, a title copy and a description copy; one a day.
7. Tell people: X and LinkedIn posts, bios, reply to comments in the first hour.

Timestamps in the YouTube description must match the final video (re-check after any re-edit).
