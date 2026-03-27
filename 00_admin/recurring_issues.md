# Recurring Issues Log

Last updated: 2026-03-27

## Purpose
Track friction patterns that appear more than once so future sessions can avoid them automatically.
When the same problem appears in two or more sessions, append an entry here.
`copilot-instructions.md` and the user-level instruction file will read this implicitly through the Automatic Improvement Rule.

## Format
Each entry is a short named block:

```
### RI-NNN — Short title
- first_seen: YYYY-MM-DD
- last_seen: YYYY-MM-DD
- pattern: what keeps happening
- fix_applied: what was done to stop it recurring (or "pending" if still open)
```

---

### RI-001 — Hardcoded model name in prompt/agent frontmatter causes validation rejection
- first_seen: 2026-03-27
- last_seen: 2026-03-27
- pattern: `.prompt.md` and `.agent.md` files with an explicit `model:` frontmatter field get rejected by the VS Code validation layer; the model identifier string is not recognised.
- fix_applied: Removed `model:` field from all agent and prompt frontmatter. Let the active VS Code model selection take effect instead. Also renamed deprecated `mode:` to `agent:` in prompt frontmatter.

---

## Pending / No Fix Yet

None.
