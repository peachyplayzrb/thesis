# Upgrades Roadmap

Last updated: 2026-04-21

## Purpose

Track the practical tooling-expansion plan for the thesis environment in execution order, with emphasis on deterministic engineering, artefact inspection, repo hygiene, and thesis-output support.

## Current Status

### Completed

#### Phase 1 - Environment and workflow baseline
- `uv`
- `pre-commit`
- `shellcheck`
- `shfmt`
- `watchexec`

#### Phase 2 - Data and experiment inspection core
- `duckdb`
- `mlr`
- `sqlite3`
- `visidata` / `vd`

#### Phase 2 operationalization baseline
- `07_implementation/README.md` now documents one canonical `duckdb` workflow for the latest BL-013 and BL-014 JSON outputs.
- `07_implementation/README.md` now documents one canonical `mlr` workflow for BL-006 score summaries.
- `07_implementation/README.md` now documents one canonical `vd` workflow for interactive BL-014 matrix inspection.
- `.vscode/tasks.json` now exposes repeatable task surfaces for those three workflows.

#### Phase 3 - Writing and diagram support (operationalized 2026-04-21)
- `pandoc` — installed via winget (`JohnMacFarlane.Pandoc`); resolves from PATH.
- `graphviz` / `dot` — installed via winget (`Graphviz.Graphviz`); NOT added to Machine PATH by installer; wrapper hard-codes fallback to `C:\Program Files\Graphviz\bin\dot.exe`.
- `mermaid-cli` / `mmdc` — installed via npm global (`@mermaid-js/mermaid-cli`); resolves from npm bin on PATH.
- `vale` — installed via winget (`errata-ai.Vale`); resolves from PATH.
- `wargs` — installed via winget (`Winix.Wargs`); parallel command runner; resolves from PATH.
- `run_tool_with_venv_fallback.ps1` ValidateSet extended to include all five tools.
- `.vscode/tasks.json` now exposes five Phase 3 task surfaces: `07: Wargs Parallel Run`, `07: Pandoc Convert Chapter (MD to DOCX)`, `07: Graphviz Render Diagram`, `07: Mermaid Render Diagram`, `07: Vale Lint Writing`.
- `07_implementation/README.md` now documents canonical commands for all five tools under "Writing and Diagram Tools".

### Deferred
- `parallel`

Reason:
No clear GNU Parallel-equivalent package source was available on this machine through the validated install paths used in this session, so it was intentionally deferred rather than replaced with a different tool silently.

## Next Steps

### Priority 1 - Finish Phase 2 operationalization
1. Decide whether to keep PowerShell-native parallelism (`ForEach-Object -Parallel`, `Start-Job`) as the standard parallel path or install a separate dedicated parallel runner later.
2. Add one bounded `sqlite3` example only if a concrete repo-facing SQLite workflow appears; do not add placeholder commands.
3. Keep the command surface small and prefer task-backed/documented workflows over ad hoc one-offs.

Suggested first commands to formalize:
- inspect latest BL-013 / BL-014 JSON with `duckdb`
- summarize CSV artefacts with `mlr`
- inspect generated tables interactively with `vd`
- query SQLite-style ad hoc experiment tables with `sqlite3` when useful

### Priority 2 - Phase 3 writing and diagram support
**COMPLETE** (2026-04-21). See Phase 3 entry in Completed section above.

### Priority 3 - Integrate upgrades into repo workflow
1. Add a short implementation-facing section to `07_implementation/README.md` or a dedicated tooling note that documents the new recommended tools.
2. Add a few canonical commands/tasks for artefact inspection, output comparison, and run-result summarization.
3. Keep the command surface small and demonstrably useful to avoid tool sprawl.

### Priority 4 - Optional quality-of-life additions
Candidate tools:
- `zellij`
- `rga`
- `rsync`
- `lsof`

These are useful, but they are lower priority than formalizing the already-installed analysis stack.

## Recommended Immediate Follow-up

If continuing execution, the next bounded tranche should be:

1. Set up a `vale` styles directory and `.vale.ini` config if prose linting on chapter drafts is wanted.
2. Create canonical `dot` and `mmd` source files for the pipeline architecture diagram.
3. Add a concrete `sqlite3` workflow only if a real SQLite-backed inspection need appears.
4. Evaluate Priority 4 optional tools (`zellij`, `rga`, `rsync`) only when they solve a concrete friction point.

## Decision Rule

Only add a new tool when at least one of the following is true:

1. It reduces repeated manual work in the thesis repo.
2. It improves reproducibility or inspection of outputs.
3. It makes a defendable engineering workflow easier to demonstrate.
4. It replaces a weaker manual process already being used.
