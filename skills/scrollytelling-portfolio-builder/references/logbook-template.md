# Logbook template (and how to build it from git)

A logbook is a dated diary the owner can read in two minutes. Build it at the end (or weekly) from the git history so the dates are true.

## Get the data

```bash
git log --reverse --format='%ad|%s' --date=format:'%Y-%m-%d %H:%M' > /tmp/log.txt
cut -d'|' -f1 /tmp/log.txt | cut -c1-10 | sort | uniq -c        # commits per day
git rev-list --count HEAD                                          # total commits
```
If the history was rewritten (filter-repo) the dates and subjects are kept. If a project spans several repos or old folders, read the oldest one too.

## Layout

```
# Logbook: "<site>"
Built over <N> calendar days, <first date> to <last date> (first commit <weekday date time>, last <...>), <M> commits on <K> of the <N> days (<days with none>).
Phase table: | Phase | Dates | What |
## Day by day
**<Weekday D Mon> (<commits>).** 2-5 sentences: what was built, what was decided, what was undone, what hurt.
...
## Numbers
days, commits, chapters, assets, test sizes, biggest lessons
```

## Style rules

- Plain words, past tense, one paragraph per day; name the big day ("ship day", "the big build day").
- Mention reverts and dead ends (they are the story).
- Do not claim hours you did not measure; use commit counts and times.
- Link the other docs at the end: process, TODO, deploy, prompts.
