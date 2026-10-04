
# SHAPES / PETRA Vision

## Identity

The architecture has two primary layers:

```text
SHAPES
    agnostic structural substrate

PETRA
    Prime Exponent Tower Recursive Algebra
    interpretation layer over SHAPES
```

PIP — the Prime Interpretation Problem — belongs inside PETRA.

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

PETRA is a pluggable interpretation layer directly over SHAPES.

Its role is to study and implement prime/exponent interpretations without feeding interpretation-specific meaning back into SHAPES ontology.

The dependency is:

```text
PETRA -> SHAPES
future interpretation -> SHAPES

SHAPES -X-> PETRA
PETRA -X-> future interpretation
```

Future interpretations may sit beside PETRA:

```text
PETRA ----------\
                 \
Future X ---------> SHAPES
Future Y --------/
```

Sibling interpretation layers do not depend on one another unless a separate future architecture explicitly introduces such a dependency.

## PIP

The Prime Interpretation Problem is PETRA's foundational interpretation problem.

It asks which prime/exponent interpretation rules over SHAPES are admissible and what properties they have.

PIP is not the SHAPES carrier.

PIP is not a sibling plugin beside PETRA.

PIP lives inside PETRA.

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
