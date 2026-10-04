
# AGENTS.md

## Purpose

This file defines how coding and research agents should work in this repository.
It is an operational contract, not a semantic specification for SHAPES or PETRA.

## Sources of truth

- `docs/reference/SPEC.md` is the sole normative source for SHAPES core semantics.
- `docs/VISION.md` describes the SHAPES/PETRA architecture and project intent; it does not override the specification.
- `ROADMAP.md` orders planned work; it does not make experimental behavior normative.
- `docs/research/` contains exploratory or historical material. Research becomes canonical only through an explicit promotion into the appropriate normative layer and corresponding implementation work.

Do not duplicate SHAPES semantics in this file. When a structural semantic question is unclear, resolve it against the canonical specification before changing code.

Historical PETRA research terminology must not be interpreted automatically as future PETRA interpretation semantics.

## Core / interpretation boundary

SHAPES is the agnostic structural core.

SHAPES owns:

- canonical recursive form;
- structural equality;
- finite child multisets;
- primitive direct parent-child incidence;
- intrinsic multiplicity;
- intrinsic `ADD` / `REMOVE`;
- structural properties derived solely from that carrier.

PETRA — Prime Exponent Tower Recursive Algebra — is reserved for a pluggable prime/exponent interpretation layer over SHAPES.

PIP — the Prime Interpretation Problem — is foundational theory inside PETRA. It is not a sibling core and is not a dependency of SHAPES.

The dependency direction is strict:

```text
PETRA -> SHAPES
future interpretation -> SHAPES

SHAPES -X-> PETRA
PETRA -X-> future interpretation
```

New SHAPES work must remain independent of:

- prime assignment;
- exponent interpretation;
- represented integer values;
- primality testing;
- factorization;
- PETRA-specific interpretation policy.

The current `petra` package, CLI, schemas, representation types, and compatibility operators predate this separation. During migration they may remain temporarily executable, but their existence does not make their PETRA-specific or representation-specific concepts part of SHAPES ontology.

## Change discipline

Before starting work:

1. inspect the current branch and repository state;
2. inspect open issues and pull requests for overlap or prerequisite work;
3. identify the canonical contract affected by the change;
4. keep one primary concern per change whenever practical.

For behavioral changes, prefer evidence and regression coverage before implementation.

Preserve an existing public contract only when the active specification or migration plan still admits it. Do not preserve an obsolete contract solely for continuity.

Verification must be proportional to scope and should include the smallest focused check that demonstrates the changed contract plus broader regression coverage when the change can affect shared behavior.

## Research discipline

Research is not implementation by default.

Before running an experiment, freeze:

- the research question;
- the scope and controlled inputs;
- the measurements or comparison axes;
- the falsification criteria;
- the possible outcome classes.

Do not add success criteria after seeing the result merely to make an experiment pass.

Record negative and partial results as first-class evidence.

A successful experiment does not automatically become:

- SHAPES core semantics;
- PETRA interpretation semantics;
- a roadmap commitment;
- production API behavior;
- an upstream or downstream integration proposal.

Promotion requires a separate explicit decision and the appropriate canonical change.

## Cross-domain design transfer

Keep these layers distinct:

1. **SHAPES semantics** — the agnostic structural core defined by `docs/reference/SPEC.md`;
2. **PETRA semantics** — prime/exponent interpretation semantics layered over SHAPES;
3. **design transfer** — applying a SHAPES- or PETRA-derived principle to another domain;
4. **integration proposal** — a concrete proposal to change this project or another project based on evidence from that transfer.

Do not describe transferred research as a SHAPES or PETRA feature unless it has been explicitly promoted into the appropriate canonical layer.

Do not involve external maintainers or present an integration proposal as established until the local evidence justifies doing so.

## Historical material

Do not mass-rename historical research merely to match the current architecture.

In particular, historical uses of PET, PETRA, `Leaf`, `Container`, `Term`, `Root`, `SPROUT`, `SHED`, `GRAFT`, `PRUNE`, prime projection, factorization experiments, or released interfaces should retain their original terminology when that terminology identifies the object actually studied at the time.

Git history, tags, releases, and archived research are the preservation mechanism for superseded architectures.

## Legacy and migration

The migration order is:

```text
current pre-separation PETRA runtime
        ↓
SHAPES agnostic runtime
        ↓
migrate structure-only dependents
        ↓
retire old structural petra package
        ↓
PETRA interpretation layer over SHAPES
```

The current `petra` runtime is not to become a permanent compatibility wrapper around SHAPES.

Temporary coexistence is permitted only as an explicit migration mechanism.

The old `petra` package disappears only after all agnostic runtime responsibilities and their dependents have migrated to SHAPES and before the new PETRA interpretation implementation is introduced.

Reuse legacy artifacts only when a current SHAPES or future PETRA requirement demonstrably needs them.

Do not preserve obsolete APIs, formats, operators, tests, probes, or compatibility layers solely for continuity.

## Agent collaboration

Prefer repository-visible evidence over assumptions or remembered state.

If another issue, pull request, branch, or research gate already owns the same concern, coordinate with that work instead of opening overlapping implementation.

When uncertainty remains, make the boundary explicit in code, tests, or research notes rather than silently choosing a convenient interpretation.
