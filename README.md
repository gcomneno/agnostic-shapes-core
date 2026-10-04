
# SHAPES core / PETRA interpretation architecture

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22741778.svg)](https://doi.org/10.5281/zenodo.22741778)

This repository is transitioning to a layered architecture:

```text
PETRA
    prime/exponent interpretation layer
    └── PIP
        Prime Interpretation Problem
        foundational theory inside PETRA
    ↓
SHAPES
    agnostic structural core
```

SHAPES is the structural substrate.

PETRA — **Prime Exponent Tower Recursive Algebra** — is an interpretation layer that depends on SHAPES.

SHAPES does not depend on PETRA.

Other future interpretation layers may depend directly on SHAPES without depending on PETRA.

## SHAPES core

The canonical carrier is the class of finite rooted non-plane forms:

```text
S ::= Node(M_f(S))
```

where `M_f(S)` is the finite-multiset constructor over SHAPES forms.

Therefore:

- there is one ontological node species;
- `Node(empty multiset)` is the unique zero-child form;
- direct parent-child incidence is primitive;
- child multiplicity is intrinsic;
- sibling order is not intrinsic;
- structural equality is rooted non-plane structural isomorphism;
- no positional rank or persistent occurrence identity participates in form identity.

The intrinsic elementary edit algebra consists of:

```text
ADD
REMOVE
```

`ADD` creates one fresh zero-child child occurrence under a selected parent occurrence.

`REMOVE` deletes one selected zero-child non-root child occurrence.

After quotienting realization-local labels by structural equality, these induce relations on SHAPES forms.

### Current SHAPES runtime representation API

The maintained SHAPES runtime also exposes state-scoped occurrence traversal:

```python
from shapes import iter_occurrences
```

`iter_occurrences(shape)` yields `(OccurrencePath, Shape)` pairs for every
occurrence in deterministic preorder over the current canonical runtime
representation.

`OccurrencePath` is a selector for one concrete `Shape` state only.

It is **not**:

- persistent occurrence identity;
- intrinsic sibling order;
- part of structural equality;
- a stable identifier across edits.

Equal sibling forms remain distinct occurrences when they correspond to
distinct child incidences. After an edit, consumers must derive paths again
from the resulting state.

The normative contract is defined by
[`docs/reference/SPEC.md`](docs/reference/SPEC.md).

## PETRA layer

PETRA is reserved for prime/exponent interpretations of already-existing SHAPES forms.

The dependency is:

```text
PETRA -> SHAPES
future interpretation -> SHAPES

SHAPES -X-> PETRA
PETRA -X-> future interpretation
```

Prime identities, exponent semantics, numeric projection, primality testing, factorization, and interpretation-specific ordering are not SHAPES core semantics.

The **Prime Interpretation Problem (PIP)** belongs inside PETRA. It studies which prime/exponent interpretation rules over SHAPES are admissible, injective, equivalent, reachable, computable, or otherwise structurally significant.

PIP does not define SHAPES.

## Current migration state

The repository still contains the released pre-separation PETRA runtime.

Today that compatibility surface includes:

- Python distribution/package `petra`;
- CLI `petra`;
- `Leaf`, `Container`, `Term`, and `Root`;
- positional ranks and addresses;
- textual `1` / `C(r0^...)` serialization;
- `petra.operator-*` JSON schemas;
- `SPROUT`, `SHED`, `GRAFT`, and `PRUNE`;
- result/witness contracts;
- Resolver code importing from `petra`.

Those interfaces remain executable during migration, but they do **not** define the new SHAPES ontology merely because they currently exist.

Runtime, package, CLI, serialization, and Resolver migration are separate implementation phases.

## Canonical sources

1. [SHAPES core specification](docs/reference/SPEC.md)
2. [SHAPES / PETRA vision](docs/VISION.md)
3. [Implementation roadmap](ROADMAP.md)
4. [Documentation map](docs/README.md)
5. [Current project status](docs/reports/STATUS.md)
6. [Current PETRA compatibility CLI reference](docs/reference/CLI.md)

`docs/reference/SPEC.md` is the sole normative source for SHAPES core semantics.

Historical and research documents retain the terminology appropriate to the architecture or experiment they originally described.

## Current PETRA compatibility CLI

The currently released runtime exposes:

```bash
petra '1' '{"schema":"petra.operator-invocation.v1","operator":"SPROUT","target":{"mode":"default"}}'
```

This command and the `petra.*` schemas belong to the pre-separation compatibility runtime.

They are not silently renamed into SHAPES contracts.

A future SHAPES CLI or serialization contract must be specified independently before becoming public API.

## Resolver

The repository also hosts `resolver/`.

Resolver currently imports the `petra` package and contains both structural and arithmetic/projection-oriented capabilities.

During the SHAPES migration:

- structure-only capabilities may migrate to SHAPES;
- numeric projection, prime assignment, `int_to_shape`, factorization-based construction, and other arithmetic interpretation behavior must not be pulled into SHAPES;
- Resolver remains a satellite until its responsibilities can be classified cleanly.

## Tests

The current default test gate remains:

```bash
pytest tests/ -q -m "not slow"
```

Until runtime migration begins, existing PETRA compatibility tests remain valid tests of the currently released implementation.

New SHAPES tests will be introduced separately when the SHAPES runtime package is created.

## Historical releases

Historical release terminology is intentionally preserved.

- `v0.1.0` through `v0.3.0` belong to historical PET.
- `v1.x` belongs to the first PETRA release line.
- `v2.0.0` begins the second PETRA major line.
- `v2.1.0`, released on 2026-10-03, promoted the agnostic carrier and intrinsic `ADD` / `REMOVE` theory while retaining the existing PETRA runtime representation and compatibility surfaces.

The SHAPES/PETRA separation is a later architectural boundary and must not rewrite the meaning of already-published releases.

## Historical and research material

Do not mass-rename `docs/research/`, archived documents, validation reports, release notes, changelog entries, DOI metadata, or citations that refer to PET or PETRA as historically defined.

Those records are evidence of how the current architecture was derived.
