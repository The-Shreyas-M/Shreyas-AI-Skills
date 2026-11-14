# AI Video Editor: how to use it (30 seconds)

1. Drop your video(s) into **Raw Footage/**.
2. In ANY Claude chat say, for example:
   > Use the AI Video Editor folder. Edit `Raw Footage/my-talk.mp4` into 3 Shorts and one cleaned long video. Show me the results, then wait.
   Claude starts one helper session inside this folder (so your chat stays cheap), edits, and tells you where the files are in **Exports/**.
3. Watch the files. Give notes one at a time ("hook louder", "cut the second part"), or say **approved**.
4. Say: *Schedule these on YouTube Shorts, one a day at 7:30 pm* (or *post now*). Claude fills the posting queue, shows you the dry-run, and only posts after you say go.

One-time setup for posting: see `posting/README.md` (create the YouTube login once with `post.py auth`).
Everything Claude must follow is in `CLAUDE.md`.

## If a chat does not know this folder
Tell it: "Read `<your workspace>/CLAUDE.md` (the path is saved in `~/.claude/ai-video-editor.json`) and follow it", or install the skill `ai-video-studio` (`python install.py` from the ai-video-editor repo).

## Starting a helper session yourself
`run-edit.ps1 "<brief>"` (Windows) runs Claude Code headless in this folder with the brief and prints only the final report.
