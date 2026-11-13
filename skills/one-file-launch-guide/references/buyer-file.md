# The buyer file (what the customer gets)

ONE offline .html, same brand look (black brushed-steel feel, steel-gradient Impact headings, yellow accent). No personal details. Structure used for "The Life-Story Website Blueprint":

1. Header: logo, title, "By <Name> x <Brand>".
2. A big yellow **"Copy the Master Prompt"** button + the master prompt in a scroll box. The customer pastes it into Claude Code (or any agent) in an empty folder; the agent interviews them a few questions at a time, creates the project folder (story outline, TODO, prompt file, logbook), tells them exactly what only they can do (reference image, avatar, accounts) and starts building at once with placeholders.
3. The guide: numbered phases (interview -> story -> art -> build -> test -> launch), the rules that prevented rework, the known traps.
4. A **Toolkit**: collapsible blocks, each with a copy button (scripts, templates, prompt files).
5. Footer: licence (personal use), support email/reply instruction, "no income promises".

Make it from markdown sources with a small Python script (`markdown` package) that wraps each `<pre>` with a copy button and embeds the logo. Keep the sources in the project: the finished html alone is hard to edit.

Test: the master-prompt copy button must put exactly the prompt text on the clipboard (compare length), every toolkit copy button works, page works offline, no console errors.
