# Agent skills for working with this theme

These are **versioned originals**. Claude Code only loads skills from
`~/.claude/skills/` (user-global) or a repo's `.claude/skills/` (project),
so a copy here is not active on its own — it's here so the work survives a
machine, and so any maintainer can pick it up.

## Installing

```sh
cp -R skills/upgrade-theme ~/.claude/skills/
```

## Keeping them in sync

The deployed copy at `~/.claude/skills/upgrade-theme/SKILL.md` and the
original here can drift, and nothing detects that automatically. If you edit
one, copy it to the other in the same change. Diff them with:

```sh
diff ~/.claude/skills/upgrade-theme/SKILL.md skills/upgrade-theme/SKILL.md
```

## What's here

- **`upgrade-theme/`** — fetches `docs/upgrading.md` from the theme's
  `origin/master` (without disturbing the submodule's checked-out state),
  triages whether a move is an *update* or the *pre-unification upgrade*, and
  runs it at a verification level matched to the size of the change. The
  authoritative procedure is `docs/upgrading.md`; this skill is the entry
  point that decides how much of it to execute.
