#!/bin/sh
# Tells the orchestrator when this session has grown large. Every turn re-reads the whole
# conversation, so a long session is the biggest cost in this workflow (measured: 84% of a bill).
# Advisory only: it prints a notice, it never blocks anything.
in=$(cat)
t=$(printf '%s' "$in" | sed -n 's/.*"transcript_path"[ ]*:[ ]*"\([^"]*\)".*/\1/p' | sed 's/\\\\/\//g')
[ -n "$t" ] && [ -f "$t" ] || exit 0
last() { tail -c 3000000 "$t" 2>/dev/null | grep -o "\"$1\":[0-9]*" | tail -1 | tr -dc 0-9; }
cr=$(last cache_read_input_tokens); cw=$(last cache_creation_input_tokens)
total=$(( ${cr:-0} + ${cw:-0} ))
[ "$total" -ge "${NP_CTX_WARN:-200000}" ] || exit 0
cat <<EOF
CONTEXT GUARD (this project's rule): this session now holds about $(( total / 1000 ))k tokens, and every turn
re-reads all of it. That, not the workers, is the largest cost here. Finish only the task in hand, bring
HANDOFF.md and TODO.md up to date, then tell the owner in one line to open a NEW session and run
/new-project:continue (or /sprint). Do not start another task in this session unless the owner says to stay.
EOF
exit 0
