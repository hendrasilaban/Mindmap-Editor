# Mindmap Editor — mind map editor for manual QA review

> Version: 1.25
Editor: **`mindmap-editor.html` v1.20** — the version is written in the header of that file itself, and
that is its only source.

## Running it

**Double-click `mindmap-editor.html`.** That's it — no server, no install.

Measured in Chrome on the original machine (2026-08-28): on `file://`, `isSecureContext` is `true` and
`showSaveFilePicker` is available — so the **Save button overwrites the opened `.mm` file**, just as
it does over localhost.

| How you open it | Save button | When to use it |
|---|---|---|
| double-click (`file://`) | **overwrites the file** (Chrome/Edge) | **default** |
| `python open_editor.py` | overwrites the file | if your browser lacks the File System Access API, or you want to go through localhost |

`open_editor.py` is **optional**. It starts a server that keeps running until `Ctrl+C`, so don't
run it unless you need it. Browsers without that API (e.g. Firefox) download a copy instead; the
editor tells you which applies in its status bar.

## From inside an IDE

| | VS Code | PyCharm |
|---|---|---|
| Open in a browser | right-click the file → *Open with Live Server* / *Reveal in File Explorer* | right-click → *Open in Browser* |
| Preview in a tab | the **Live Preview** extension (Microsoft), or `Simple Browser: Show` + `open_editor.py` | built-in preview (JCEF), depending on version |
| Simplest | open the HTML file directly in a browser — **no server needed** | same |

**`.mm` as a visual editor tab inside the IDE** (Ctrl+S overwrites the file) would need a dedicated
VS Code extension (`CustomTextEditorProvider` + webview) or a JetBrains plugin. Not built, on
purpose: the browser route above gives the same result without maintaining two extensions.

## Keys

| | |
|---|---|
| **Open .mm / .mup** | `.mm` is read the way the consumer reads it (`draft-template.md` §2/§7): `TEXT`, or `<richcontent TYPE="NODE">` if `TEXT` is missing, and a `button_ok` / `checked` / `yes` icon on a leaf becomes ✅. `.mup` (MindMup) is read from each node's `title`, with children in MindMup's order; a `.mup` map with more than one root is rejected, listing the root names. Saves `.mm` only: after opening a `.mup`, Save asks for a new `.mm` name and the original `.mup` is never overwritten. Unreadable files are rejected with the reason |
| **Mouse wheel** | pan the map · **Ctrl+Wheel** zoom · **Shift+Wheel** pan horizontally |
| **PgUp / PgDn** | scroll one screen · **Home** fit view |
| **Double-click** / **F2** | edit text |
| **Shift+Enter** | new line — this is how you write an `INT` bundle (numbered list) |
| **Enter** | sibling node · **Tab** child node — on the root: sub process · on the E2E folder: test case · on a sub process, Additional or Archive: entry point · on an entry point: type node |
| **t** | cycle the type node's rung (UI → INT → SYS → E2E) |
| **r** | mark ✅ regression — only on SYS and E2E test cases; refused on UI / INT, but an existing ✅ there can be removed |
| **[** **]** | narrow / widen the selected node — or drag the handle on its right side |
| **Shift+[** **Shift+]** | default width of ALL nodes |
| **0** | reset the selected node's width |
| **Del** delete · **Space** fold · **↑↓←→** move · **Ctrl+S** save |

## Large maps

Real drafts can hold hundreds of test cases. What the editor does automatically:

| | |
|---|---|
| over 60 TCs | opens **compact** — branches below type nodes are folded, TC counts stay visible |
| autofit zoom | held at a minimum of **35%** so text stays readable, instead of forcing everything to fit |
| window resized | refits automatically — as long as you haven't panned / zoomed; after that press **Home** |
| browsing | **the mouse wheel pans**; `Ctrl+wheel` zooms |
| expanding everything | the **Expand all** button |

Measured example (a legacy draft with 218 leaves): opens at 59% with 25 readable nodes and 16 rungs
folded; after "Expand all" it becomes 286 nodes at 35%.

## The draft tree

The editor reads and writes the same tree as Generate Draft TC
(`.claude/skills/generate-draft-tc/references/draft-template.md` §1):

```
FEATURE (Total: N TCs)
├── <sub process> (n)             <- NOT numbered
│   └── 1. <page / entry point> (n) <- numbered continuously across the feature = page count
│       └── UI · INT · SYS (n)
│           └── test case
├── E2E (n)                        <- End to End cases only
│   └── test case                  <- DIRECTLY: one full journey through every sub process of the main flow
├── Additional (n)                 <- dependency cases: FDS, event tracker, …
│   └── <topic> (n) → type → test case
└── Archive (n)                    <- old cases that are no longer compatible
    └── <original entry point> (n) → type → test case
```

E2E, Additional and Archive are recognized by their POSITION (direct children of the root), are not
numbered, and are always present — possibly empty. The starter map the editor opens without a file
already contains all three. The E2E folder has no entry points or type nodes: its test cases sit
directly inside it, and the folder itself is their rung.

## What this editor guards for you

The following four mistakes make test cases **disappear without a report** in the downstream
sub-project. This editor prevents or flags them:

| Mistake | What the editor does |
|---|---|
| leaf outside a type node | **Tab** on an entry point creates a *type node* (`UI`, change it with `t`), not an empty node; **Tab** on the E2E folder creates a test case directly — so a leaf is never born outside its rung |
| stale `(n)` and `(Total: N TCs)` counts | **recomputed on every save** |
| newline turned into a space (broken `INT` bundle) | newlines are always written as `&#10;` |
| colors on leaves | never written — colors only on sub processes, folders, entry points and type nodes (cosmetic) |

Plus the **Pre-check**: missing or duplicate E2E / Additional / Archive folders, a draft with no sub
process, a type node without an entry point level, an entry point in two sub processes, a sub process
or entry point with no test cases, nodes in the E2E folder that are not test cases (entry points or
type nodes), an E2E type node in a sub process or Additional, duplicate titles, leaves outside a
type node, bundles over 10 lines, folded bundles, multi-line non-INT leaves, sub processes or entry
points named like a rung, and nodes with no text.

🔴 **The pre-check is not the authority.** The deciders are still
`.claude/scripts/validate_draft.py` (Prove) and
`.claude/scripts/review_result_draft.py` (Audit). The pre-check does
not check naming, coverage, or basis.

🔴 **Every manual edit must be re-Proved and re-Audited:**

```
python .claude/scripts/validate_draft.py "../Draft to Manual Test Case/requirements/<platform>/Draft_<feature>_v<version>.mm"
python .claude/scripts/review_result_draft.py --platform <platform> --feature <feature>
```

This is not a formality: editing a draft makes the `trace` **stale**, and a stale trace means the
coverage numbers are computed against the wrong basis. The Audit reports it as `STALE TRACE` and
refuses to declare COMPLETE.

## What this editor does NOT do

- it does not write Steps and Expected Results — those belong to the downstream sub-project;
- it does not know the requirement index, so it cannot tell whether a leaf has a basis;
- it does not SAVE any format other than `.mm` — this project's format is `.mm`. `.mup` is only
  opened to be converted to `.mm` (this copy is standalone; the editor in the pipeline's `tools/`
  stays `.mm`-only);
- **its pre-check is not Prove.** What Prove (`validate_draft.py`) does and the editor doesn't:
  reject duplicate titles, leaves outside a type node, and folded bundles. A legacy draft QA prepares
  here is processed by Review Requirement only if Prove reads it as a legacy draft
  (`validate_draft.py --baseline`);
- it does not save node widths into the `.mm` — that is a display preference, stored in localStorage
  per file. A colleague opening the same file uses their own default widths.

## Tested

Tested automatically in real Chrome (headless, via the DevTools Protocol):

| Test | Result |
|---|---|
| text editing: double-click, type, commit | edit mode entered, caret inside the text, typing saved |
| node width (`[` `]`) | changes |
| large map (`Dashboard`, 218 leaves) | opens compact at 59%, wheel pans, `Ctrl+wheel` zooms |
| **node overlap** | **0** — compact, fully expanded, and after manual folding |
| fresh clone (folder copied, new browser profile) | loads a real `.mm` with no JS errors |
| importing FreeMind-style `.mm` (`richcontent`, ✅ icon) — the consumer's `draft_mm_shapes.mm` fixture plus one `richcontent` bundle | titles, case count, and regression IDENTICAL to the consumer's reader (`parse_draft.py`, run read-only as the reference) |
| importing `.mup` (2026-11-18, headless Chrome, **hand-made** fixtures: formatVersion 3, 2, no formatVersion, with BOM, multiple roots, broken JSON) | tree, rank order (positive then negative), multi-line INT leaves and ✅ read correctly; `.mup` → `.mm` → reopen = same tree; multiple roots and broken JSON rejected, with the open map unchanged; Save after `.mup` suggests `Draft_x.mm` and never writes to the `.mup` |
| text inside node boxes (2026-11-18, `Referensi/test mup`, headless Chrome) | before v1.19: 33 of 48 nodes overflowed when opened compact (the hidden-TC line was wider than the `UI`/`INT`/`SYS` box). After: **0** compact, fully expanded, and with folded nodes narrowed to 90px; overlap still **0** |
| refit on window resize | 1280×700 → 1920×1000: zoom adjusts; after using the mouse wheel, resizing doesn't move the view; **Home** restores autofit |
| importing a real QA `.mup` (2026-11-18, `Referensi/test mup` — formatVersion 3, NO extension, 231 nodes, 125 leaves) | 231/231 nodes and 125/125 leaves, order and text IDENTICAL to the JSON; `.mup` → `.mm` → reopen = 231 nodes; no JS errors. Not carried into `.mm`: colors (`#adff2f` on 24 section/type nodes), the root note, MindMup fold state. **The Open dialog on macOS has not been tried** |

The export function was tested headless with node (16 tests: newline escaping, recomputed counts,
section numbering, no placeholders), then the resulting `.mm` was fed to `validate_draft.py` →
**PROVEN**, and the consumer reader round trip passed **5/5 cases**.

The tests above were run on the Indonesian UI (v1.19 and earlier). v1.20 translates the interface
and comments to English; the code logic is unchanged.

🔴 **What can't be proven headless:** how the interaction feels — layout, focus while editing,
dragging the width handle — is judged by QA while using it. Report anything that misbehaves.
