# Run one edit job in a fresh headless Claude Code session inside this folder.
# Usage:  .\run-edit.ps1 "Edit 'Raw Footage\talk.mp4' into 3 Shorts. Report file paths only."
# The session reads CLAUDE.md here, does the heavy work, and prints a short report.
param([Parameter(Mandatory = $true)][string]$Brief)
Set-Location $PSScriptRoot
$prompt = "Read CLAUDE.md in this folder and follow it. Job: $Brief`nFinish with a report of at most 150 words: a table file|length|title, and anything uncertain. Do not post anything."
claude -p $prompt --permission-mode acceptEdits
