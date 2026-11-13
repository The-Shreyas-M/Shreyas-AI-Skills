"""Build a single self-contained "do these steps in order" HTML guide from a JSON spec.

Usage: python build_guide.py guide.json            (writes the html named in spec["out"])

Result: ONE .html file (all images/files embedded as base64, works offline, no libraries):
 - sticky top bar with link inputs (spec["variables"]) + Sync button + "3 of 7 done" progress
 - numbered step cards with a tick box (remembered in localStorage)
 - green Copy buttons for every text block, yellow Download buttons for images/files
 - {VARIABLE} placeholders in copy blocks update live when the user pastes their real links and presses Sync
See ../references/spec-format.md and ../assets/example-guide.json
"""
import base64, html, json, mimetypes, os, re, sys

spec_path = os.path.abspath(sys.argv[1])
S = json.load(open(spec_path, encoding="utf-8"))
base = os.path.dirname(spec_path)
esc = html.escape
uid = [0]


def path(p):
    return p if os.path.isabs(p) else os.path.join(base, p)


def data_uri(p):
    p = path(p)
    mime = mimetypes.guess_type(p)[0] or "application/octet-stream"
    return f"data:{mime};base64," + base64.b64encode(open(p, "rb").read()).decode()


def block(b):
    t = b["type"]
    if t == "html":
        return b["html"]
    if t == "note":
        return f'<p class="note">{esc(b["text"])}</p>'
    if t == "copy":
        uid[0] += 1
        i = f"t{uid[0]}"
        pre = f'<p class="cl">{esc(b["caption"])}</p>' if b.get("caption") else ""
        return (f'{pre}<div class="blk"><pre id="{i}" class="tpl">{esc(b["text"])}</pre>'
                f'<button class="cb" data-t="{i}">{esc(b.get("label", "Copy"))}</button></div>')
    if t == "download":
        a = "".join(f'<a class="dl" download="{esc(it.get("name") or os.path.basename(it["file"]))}" '
                    f'href="{data_uri(it["file"])}">⬇ {esc(it["label"])}</a>' for it in b["items"])
        return f'<div class="grid">{a}</div>'
    if t == "image":
        return f'<img class="shot" src="{data_uri(b["file"])}" alt="{esc(b.get("alt", ""))}">'
    raise SystemExit(f"unknown block type {t}")


steps_html = ""
for n, st in enumerate(S["steps"], 1):
    mins = f' <span class="min">{st["minutes"]} min</span>' if st.get("minutes") else ""
    body = "".join(block(b) for b in st["blocks"])
    steps_html += (f'<section class="step"><label class="hd"><input type="checkbox" class="ck" data-k="{esc(st["id"])}">'
                   f'<span class="n">{n}</span><span class="tt">{esc(st["title"])}{mins}</span></label>'
                   f'<div class="bd">{body}</div></section>')

vars_ = S.get("variables", {})
bar_inputs = "".join(f'<div><label>{esc(v["label"])}</label><input class="var" data-var="{esc(k)}" value="{esc(v.get("default", ""))}"></div>'
                     for k, v in vars_.items())
bar_btn = '<button id="sync">Sync</button>' if vars_ else ""
logo = f'<img src="{data_uri(S["logo"])}" alt="">' if S.get("logo") else ""
acc = S.get("accent", "#ffd400")

CSS = """
:root{--bg:#050506;--card:#101114;--line:#2a2d33;--tx:#e8eaed;--mut:#9aa0a8;--acc:__ACC__}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--tx);font:16px/1.65 'Segoe UI',system-ui,Arial,sans-serif}
.wrap{max-width:860px;margin:0 auto;padding:24px 18px 80px}
h1{font-family:Impact,'Arial Black',sans-serif;text-transform:uppercase;font-size:44px;line-height:1.1;margin:.2em 0;background:linear-gradient(180deg,#fff,#9aa0a8);-webkit-background-clip:text;background-clip:text;color:transparent}
p,li{color:#cfd3d8}a{color:var(--acc)}code{background:#1a1c20;padding:1px 6px;border-radius:5px;font-size:.92em;color:#ffe680}
.top{display:flex;align-items:center;gap:14px;margin-bottom:6px}.top img{width:64px;height:64px;border-radius:12px;border:1px solid var(--line)}
.by{color:var(--mut);font:14px Consolas,monospace;letter-spacing:.18em;text-transform:uppercase}
.linkbar{position:sticky;top:0;z-index:5;background:#050506ee;border-bottom:1px solid var(--line);padding:10px 18px;display:flex;gap:10px;flex-wrap:wrap;align-items:end}
.linkbar label{font-size:11px;color:var(--acc);text-transform:uppercase;font-weight:700;display:block}
.linkbar input{background:#101114;border:1px solid var(--line);color:#7dffb0;border-radius:8px;padding:8px;width:300px;max-width:100%;font:12px Consolas,monospace}
.linkbar button{background:var(--acc);color:#000;border:0;border-radius:8px;padding:9px 16px;font-weight:800;cursor:pointer}
.prog{color:var(--acc);font-weight:800}
.step{background:var(--card);border:1px solid var(--line);border-radius:16px;margin:18px 0;overflow:hidden}.step.done{opacity:.55}
.hd{display:flex;gap:12px;align-items:center;padding:16px 18px;cursor:pointer}.ck{width:22px;height:22px;accent-color:#10b981}
.n{background:var(--acc);color:#000;font-weight:900;border-radius:50%;min-width:30px;height:30px;display:grid;place-items:center}
.tt{font-size:19px;font-weight:800}.min{font-size:13px;color:var(--mut);font-weight:600;margin-left:8px}
.bd{padding:0 18px 18px}.blk{position:relative;margin:10px 0}.cl{margin:.8em 0 .2em;font-weight:700}
pre{background:#0b0c0e;border:1px solid var(--line);border-left:4px solid var(--acc);border-radius:10px;padding:14px 90px 14px 14px;overflow:auto;max-height:240px;white-space:pre-wrap;word-wrap:break-word;font:13px/1.55 Consolas,monospace;color:#d6d9de;margin:0}
.cb{position:absolute;top:8px;right:8px;background:#059669;color:#fff;border:0;border-radius:8px;padding:6px 12px;font-weight:700;cursor:pointer}.cb.ok{background:var(--acc);color:#000}
.grid{display:flex;flex-wrap:wrap;gap:10px;margin:10px 0}.dl{background:var(--acc);color:#000;font-weight:800;text-decoration:none;border-radius:10px;padding:10px 14px;font-size:14px}
.note{color:var(--mut);font-size:14px}.shot{max-width:100%;border-radius:10px;border:1px solid var(--line)}
@media(max-width:600px){h1{font-size:32px}}
""".replace("__ACC__", acc)

JS = """
function ls(k,v){try{if(v===undefined)return localStorage.getItem(k);localStorage.setItem(k,v)}catch(e){return null}}
var V=[].slice.call(document.querySelectorAll('.var'));V.forEach(function(i){i.value=ls('v_'+i.dataset.var)||i.value});
document.querySelectorAll('.tpl').forEach(function(p){p.dataset.tpl=p.textContent});
function render(){document.querySelectorAll('.tpl').forEach(function(p){var s=p.dataset.tpl;V.forEach(function(i){s=s.split('{'+i.dataset.var+'}').join(i.value.trim())});p.textContent=s})}
var sy=document.getElementById('sync');if(sy)sy.onclick=function(){V.forEach(function(i){ls('v_'+i.dataset.var,i.value.trim())});render()};render();
document.addEventListener('click',function(e){var b=e.target.closest('.cb');if(!b)return;var t=document.getElementById(b.dataset.t).textContent;
 var done=function(){var o=b.textContent;b.classList.add('ok');b.textContent='Copied!';setTimeout(function(){b.classList.remove('ok');b.textContent=o},1300)};
 function fb(){var a=document.createElement('textarea');a.value=t;document.body.appendChild(a);a.select();try{document.execCommand('copy')}catch(x){}document.body.removeChild(a);done()}
 if(navigator.clipboard&&window.isSecureContext)navigator.clipboard.writeText(t).then(done,fb);else fb()});
function upd(){var n=0,t=0;document.querySelectorAll('.ck').forEach(function(c){t++;if(c.checked)n++;c.closest('.step').classList.toggle('done',c.checked);ls('k_'+c.dataset.k,c.checked?'1':'0')});document.getElementById('prog').textContent=n+' of '+t+' done'}
document.querySelectorAll('.ck').forEach(function(c){c.checked=ls('k_'+c.dataset.k)==='1';c.onchange=upd});upd();
"""

page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(S.get("page_title", S["title"]))}</title><style>{CSS}</style></head><body>
<div class="linkbar">{bar_inputs}{bar_btn}<span class="prog" id="prog"></span></div>
<div class="wrap"><div class="top">{logo}<div class="by">{esc(S.get("brand", ""))}</div></div>
<h1>{esc(S["title"])}</h1>{S.get("intro", "")}
{steps_html}
</div><script>{JS}</script></body></html>"""
out = path(S["out"])
open(out, "w", encoding="utf-8").write(page)
print(f"wrote {out}  {len(page) // 1024} KB, {len(S['steps'])} steps")
