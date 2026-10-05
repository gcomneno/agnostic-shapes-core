
# Agnostic SHAPES Core

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23161215.svg)](https://doi.org/10.5281/zenodo.23161215)

**ASHES** is the informal nickname for the Agnostic SHAPES Core project.

This repository hosts the interpretation-agnostic SHAPES structural core
together with maintained pluggable interpretation layers and structural
satellites.

Its architecture is:

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

The normative SHAPES contract is defined by
[`docs/reference/SPEC.md`](docs/reference/SPEC.md).

The normative PETRA interpretation contract is defined separately by
[`docs/reference/PETRA.md`](docs/reference/PETRA.md).

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

## Current architecture state

The pre-separation structural `petra` runtime has been retired.

The maintained structural runtime is `shapes`, implementing the agnostic
SHAPES core defined by `docs/reference/SPEC.md`.

The maintained PETRA package is now a pluggable prime/exponent interpretation
layer over SHAPES. Its first maintained executable policy is LRPE.

PETRA does not own or define the SHAPES carrier.

The maintained Resolver satellite depends on SHAPES through:

```text
resolver.shapes_search
resolver.shapes_distance
resolver.shapes_verify
```

Other interpretation layers may be added directly over SHAPES without
depending on PETRA.

## Canonical sources

1. [SHAPES core specification](docs/reference/SPEC.md)
2. [SHAPES / PETRA vision](docs/VISION.md)
3. [Implementation roadmap](ROADMAP.md)
4. [Documentation map](docs/README.md)
5. [Current project status](docs/reports/STATUS.md)

`docs/reference/SPEC.md` is the sole normative source for SHAPES core semantics.

Historical and research documents retain the terminology appropriate to the architecture or experiment they originally described.

## PETRA runtime status

The pre-separation PETRA CLI and its `petra.*` schemas are no longer part of
the maintained executable runtime.

Their historical contracts remain available through repository history,
release artifacts, and historical documentation.

No SHAPES CLI, parser, serializer, or schema namespace has been admitted by
the current specification.

## Resolver

Resolver is a satellite over SHAPES.

Its maintained structural runtime consists of:

```text
resolver.shapes_search
resolver.shapes_distance
resolver.shapes_verify
```

The pre-separation PETRA-coupled Resolver runtime has been retired.

## Tests

The maintained test gate is:

```bash
pytest -q -m "not slow"
```

The suite now validates the SHAPES runtime, maintained satellites, and active
documentation/report contracts. Historical PETRA compatibility behavior is no
longer kept executable solely for continuity.

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
