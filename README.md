# education — the pages SITE-MAP.md specified

`SITE-MAP.md` is 435 lines and **live on the site**. It specifies a twelve-section education
site whose routes all return 404: `/concepts/`, `/crates/`, `/build/`, `/play/`.

This is those pages, built to the spec, as a drop-in directory. The design tokens in
`assets/site.css` are lifted from the live site's own `:root` block so they look like the
same site rather than something bolted onto it.

```
index.html                          landing
concepts/                           the six, in dependency order
  ternary-conservation/             live γ+η=C calculator
  bottle-protocol/                  live envelope builder
  agent-lifecycle/                  live lifecycle simulator
  harness/                          the build→fail→vectorize loop
  conservation-law/                 the Z₃ isomorphism, and where it stops
  wavelet-decomposition/            bands
crates/                            generated from the org, not hand-maintained
build/                              four steps, plus the canary porting table
play/                               the six opcodes, live
check.py                            the checker
```

## Run the checker

```
python3 check.py
```

9/9 across 11 pages: internal links resolve, host-side links are declared as such rather
than counted as local, the stylesheet is linked everywhere, all six inline scripts parse,
the interactive handlers exist, and no page references the non-existent GitHub account.

The checker itself had two defects on its first run, both found by itself:
`node --check /dev/stdin` cannot read from a pipe in this Node build, and treating
host-side links as local produced three false failures. An instrument that cannot
distinguish "this page is broken" from "my check is wrong" is the failure mode this whole
session has been about.

## The interactive parts are real

- **Conservation calculator** — the spec's arithmetic in the page, with a refusal when
  γ+η leaves `{-1,0,+1}`, and a state classifier that rejects non-ternary input.
- **Bottle builder** — real envelope, real size accounting, demonstrating that the
  envelope does not grow with the payload.
- **Lifecycle simulator** — the four states, with suspension buffering and termination
  refusing.
- **Crates catalog** — generated from the GitHub API, forks excluded, because a vendored
  copy of llvm-project is not fleet work.
- **Playground** — BIND / LINK / TICK / FORGET over a real graph with a witness per op.

No trackers, no accounts, **no network calls** — everything that moves, moves in the page.

## Deploying

These are drop-in files. They need to land in whatever repository serves
`superinstance.dev` — which is still not identified, and is the one thing blocking the
`browse.html` fix in `site-repair/DIAGNOSIS.md`.
