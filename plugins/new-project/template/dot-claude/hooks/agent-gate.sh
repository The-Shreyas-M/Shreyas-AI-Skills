#!/bin/sh
# Blocks Claude subagent spawns (Agent tool) in this project unless an exception is on record.
# Free models through `opencode run` are the default workers - see docs/WORKFLOW.md.
cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || exit 0
# No opencode on this machine (cloud session, other machine): Claude subagents are allowed.
found=0
command -v opencode >/dev/null 2>&1 && found=1
for p in "$APPDATA/npm/opencode" "$APPDATA/npm/opencode.cmd" "$HOME/.opencode/bin/opencode" "$HOME/.npm-global/bin/opencode" /usr/local/bin/opencode /opt/homebrew/bin/opencode; do
  [ -e "$p" ] && found=1
done
[ "$found" = 1 ] || exit 0
# An exception was recorded by the orchestrator: allowed.
[ -s .oc/ALLOW_CLAUDE_AGENT ] && exit 0
cat >&2 <<EOF
BLOCKED by this project's rule: Claude subagents cost 60k+ tokens of the owner's plan per spawn.
Use a free model instead:  opencode run  through the Bash tool (default model opencode/beam-free).
Command and brief format: docs/WORKFLOW.md -> "Running opencode". That is what "delegate" and "subagent" mean here.
A Claude subagent is allowed only for: (1) opencode failed its failure ladder on this task, (2) client/employer
code, (3) the task needs a Claude-only tool you cannot use yourself. If one applies, write the task and the
reason in one line into .oc/ALLOW_CLAUDE_AGENT, tell the owner, spawn once, then delete that file.
For case (3) use model haiku: brief it to save what it reads into files under .oc/ and reply in 150 words.
EOF
exit 2
