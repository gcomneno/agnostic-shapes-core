
# SHAPES / PETRA Vision

## Identity

The architecture separates structural ontology, faithful representation, and interpretation semantics:

```text
SHAPES
    agnostic structural substrate

    ↓ faithful Tensor View

STR
    Structural Tensor Representation

    ↓ interpretation-specific LAMBDA

interpretations
    PETRA
    future interpretation layers
```

PIP — the Prime Interpretation Problem — belongs inside PETRA.

STR is a promoted common representation boundary, but it is not yet mandatory
for every interpretation. Direct interpretation from SHAPES remains
architecturally admissible unless a specific interpretation contract states
otherwise.

## Foundational separation

The research programme originally discovered its structural carrier while working under the PETRA name.

The promoted evidence now supports a stronger separation.

SHAPES owns form.

PETRA assigns one particular family of external meanings to form.

Therefore:

```text
shape first
    ↓
structural equality
    ↓
intrinsic structural edits
    ↓
optional interpretation
```

not:

```text
prime/exponent meaning
    ↓
structure
```

## SHAPES

SHAPES is the interpretation-agnostic core.

Its canonical forms are finite rooted non-plane structures with:

- one node species;
- finite child multisets;
- primitive direct parent-child incidence;
- intrinsic child multiplicity;
- no intrinsic sibling order;
- no persistent occurrence identity;
- recursive structural equality.

The zero-child form is the arity-zero case of the same node species.

The intrinsic elementary edit directions are:

```text
ADD
REMOVE
```

No prime, exponent, integer, factorization, or arithmetic interpretation is required to construct, compare, or edit a SHAPES form.

## PETRA

PETRA means **Prime Exponent Tower Recursive Algebra**.

PETRA is a pluggable prime/exponent interpretation layer over SHAPES.

Its role is to study and implement prime/exponent interpretations without feeding interpretation-specific meaning back into SHAPES ontology or STR.

The promoted common representation path is:

```text
SHAPES
    ↓
Tensor View
    ↓
STR
    ↓ Λ_PETRA
PETRA semantic domain
```

For the maintained LRPE policy, factorization through STR is proved:

```text
LRPE = Λ_LRPE ∘ C
```

where:

```text
C : SHAPES -> STR
Λ_LRPE : STR -> N+
```

This does not yet make STR mandatory for every interpretation. Direct
interpretation from SHAPES remains admissible.

The architectural dependency remains one-way.

An interpretation may depend directly on SHAPES:

```text
interpretation -> SHAPES
```

or may use the promoted representation path:

```text
interpretation -> STR / Tensor View -> SHAPES
```

In either case:

```text
SHAPES -X-> STR
SHAPES -X-> PETRA
STR -X-> PETRA
PETRA -X-> future interpretation
```

Future interpretations may sit beside PETRA and may use the promoted STR /
LAMBDA boundary when appropriate.

Sibling interpretation layers do not depend on one another unless a separate
future architecture explicitly introduces such a dependency.

## PIP

The Prime Interpretation Problem is PETRA's foundational interpretation problem.

It asks which prime/exponent interpretation rules over SHAPES are admissible and what properties they have.

PIP is not the SHAPES carrier.

PIP is not a sibling plugin beside PETRA.

PIP lives inside PETRA.

## Promoted structural representation boundary

Tensor View is the promoted faithful transduction from SHAPES into STR.

STR carries the finite rooted structural-type quotient and child multiplicity
relations without interpretation-specific meaning.

LAMBDA is the promoted interpretation contract over STR:

```text
Λ_I : STR -> D_I
```

for interpretations using this boundary.

The architecture does not currently require every interpretation to factor
through STR.

Operational History remains orthogonal to default state interpretation.

The accepted decision is recorded in:

```text
docs/architecture/0001-str-lambda-interpretation-boundary.md
```

## Representation

Runtime representations may require:

- deterministic serialization;
- selectors or addresses;
- canonical rendering;
- traversal rules;
- witnesses;
- API-specific result types.

Those are engineering interfaces over SHAPES.

They do not become structural ontology merely because a runtime needs them.

In particular, the currently released `Leaf / Container / Term / Root` representation, positional ranks, `^` slots, and `SPROUT / SHED / GRAFT / PRUNE` contracts belong to the pre-separation PETRA compatibility runtime.

Their future fate must be decided explicitly during migration.

## Resolver

Resolver is a satellite.

Structure-only Resolver capabilities may migrate to SHAPES.

Arithmetic and prime-related behavior belongs outside SHAPES and is a candidate for PETRA or another interpretation/analytic layer.

Resolver must not force numeric projection into SHAPES.

## Historical continuity

The architecture changes prospectively.

It does not rewrite historical evidence.

Published PET and PETRA releases, research notes, validation reports, experiments, DOI metadata, and citations retain the names and contracts under which they were produced.

## Engineering principle

Keep the dependency graph honest.

If a concept requires primes or exponents, it is not SHAPES merely because it originated in the same repository.

If a concept is purely structural, PETRA should consume it from SHAPES rather than own a duplicate.

The intended long-term dependency is simple:

```text
interpretations
      ↓
    SHAPES
```
