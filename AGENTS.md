# AGENTS.md

Academic assignment (IA02) comparing DFS vs DLS on graphs. Pure stdlib Python, no
dependencies, no build. Repo root **is** the project root (the README's "pasta
`ia02/`" is stale — the directory is `dfs_dls`). Everything below was verified by
running it.

## Commands

```bash
python main.py                    # comparison table + results/comparison.csv  (<1s)
python main.py --demo             # step-by-step demo on the weighted graph
python main.py --web              # regenerates web/data.js
python -m unittest -v             # 17 tests, no deps  (equivalently: python -m pytest -q)
```

Focused runs:

```bash
python -m unittest tests.test_search.TestDFS -v
python -m pytest tests/test_search.py -k cutoff
```

**Always run from the repo root.** Imports are absolute (`from algorithms import dfs`)
and there is no installable package, no `pyproject.toml`. `python -m unittest` from
any other directory silently reports `Ran 0 tests` and still exits 0 — a false green.
`python /abs/path/main.py` does work from anywhere, but writes `results/` relative to
the *current* directory.

There is **no linter, formatter, or typechecker** configured (no ruff/black/mypy,
no `pyproject.toml`, no pre-commit). Don't add one uninvited; the style is plain
PEP 8 with type hints on public signatures.

## Language

Code, docstrings, comments, README, `SearchResult.status` values (`encontrado`,
`corte (limite)`, `sem solução`), CSV headers and the whole web UI are **pt-BR**.
Match it in anything you add, including user-facing strings and commit messages.

## Layering (enforced by convention, not by tooling)

```
experiments ──► algorithms ──► models
     └────────► generators ──► models
```

- `models/` imports nothing from the project.
- `algorithms/` must **not** import `Graph`. It only knows the `StateSpace`
  protocol: `successors(state) -> Iterable[(next_state, cost)]`. Keep new
  algorithms against that interface so a game/state-machine space can use them.
- Only `experiments/` is allowed to know everything.
- States must be **hashable** — DFS stores them in a `set`, DLS stores the whole
  path tuple in its frontier.

## Semantics that look like bugs but are intentional

These are the graded content of the assignment. Do not "clean them up":

- **DFS is graph search, DLS is tree search.** DFS keeps a global `visited` set
  (first pop wins; later pops are skipped). DLS has *no* global visited — it checks
  `nxt not in path`, so a state can be re-expanded via other branches. That
  asymmetry is exactly what produces O(V+E) vs O(b^l). Never unify them.
- **DLS `cutoff` is set only when a node at the limit actually had successors**
  (`algorithms/dls.py`). `status` is derived: found → `encontrado`, else
  `corte (limite)` if cutoff, else `sem solução`.
- **`nodes_explored` = popped off the frontier and tested as goal**, identical in
  both algorithms. Increment points differ (`dfs.py` after the visited check,
  `dls.py` on every pop) but the meaning is the same — keep it that way.
- **Neighbors are pushed with `reversed(...)`** so the first successor pops first,
  matching a recursive DFS. Reordering changes every reported path and breaks
  `test_finds_path_and_metrics` / `test_within_limit`.
- `experiments/runner.py:run_one` times and measures memory in **separate runs** —
  `tracemalloc` slows the code, so it must not run during timing. Don't merge them.
- `Graph()` defaults to `is_directed=True`.
- Undirected generation only iterates `i < j`; without that the effective edge
  probability becomes `2p - p²` (guarded by `test_undirected_probability`).
- `Problem.depth_limit=None` triggers auto-estimation via
  `algorithms/depth_limit.py` in `__post_init__`.
- `experiments/problems.py` is the **fixed problem set required by the assignment**
  with fixed seeds. Changing n/p/seed rewrites the graded results table — change it
  only if asked, and update the README table with it.

## Web visualization

- `web/index.html` is **one self-contained file**: inline `<style>` + inline
  `<script>`, vanilla JS + SVG, no npm/bundler/build step. Keep it that way.
- The page does **not** reimplement the algorithms. It animates `trace` records
  that Python produced. Contract: `dfs(space, start, goal, trace=...)` and
  `dls(..., trace=...)` append one dict per expansion via
  `algorithms/tracing.record_step` (no-op when `trace is None`).
- `web/data.js` schema: `window.SEARCH_DATA = { problems: [...] }`; per problem,
  `dfs` is a single result object and `dls` is an **object keyed by limit**, which
  the JS indexes as `p.dls[S.limit]`. Keys are camelCase (`nodesExplored`,
  `maxFrontier`, `timeMs`, `memoryKiB`) — see `export_web.py:result_to_dict`.
- `export_problem` runs DLS for limits `0 .. max(estimatedLimit, optimumDepth) + 4`
  and stores every one; the slider just picks among them.
- Graphs over `MAX_NODES_TO_ANIMATE = 150` export **metrics only**: `animate: false`,
  empty `nodes`/`edges`, no `trace`. The JS branches on `p.animate` — keep that flag
  in sync when changing the threshold.
- `export()` deliberately drops the `custos (l=1)` problem because the limit slider
  already covers it.
- Open with `file://` (plain `<script src="data.js">`, no ES modules). Only the
  Google Fonts link needs network; everything else is local.
- The page is a **9-section presentation deck** (`<main> > section.slide`, one
  screen each, `scroll-snap`), written in pt-BR and without the `[n]` reference
  brackets. Sections 1–8 are the conceptual content; the 9th is the
  visualization above, unchanged in behavior. Section accents come from
  `t-dfs` / `t-dls` (or the default ink).
- Deck navigation is a **second IIFE** after the visualization one. It owns
  `↑ ↓ PgUp PgDn Home End` and `← →` *outside* the demo slide; inside it those two
  arrows stay with the search. The `keydown` listener is registered in the
  **capture** phase so it can `stopImmediatePropagation()` before the
  visualization handler, which checks `document.body.dataset.slide` (written by
  the deck's `sync()`).
- Mandatory `scroll-snap` interrupts smooth scrolling across several sections, so
  `jump()` only animates single-section moves; longer jumps are instant.
- Every section must fit a 768px-tall viewport: it is verified by measuring
  `section.scrollHeight - innerHeight` at 1366×768, 1600×900 and 1920×1080.

## Repo hygiene

- There is **no `.gitignore`**, so `__pycache__/`, `results/`, and `.pytest_cache/`
  show up as untracked. Don't `git add .` blindly.
- `web/data.js` is **tracked and generated** (~256 KB, one line). Regenerating it
  with `python main.py --web` *always* produces a diff, because it embeds measured
  `timeMs`/`memoryKiB`. Regenerate only when the export schema or the fixed problems
  actually change, and expect an unreadable single-line diff.
- `results/comparison.csv` is generated and untracked.
- Work on `main`; single-commit history so far.
