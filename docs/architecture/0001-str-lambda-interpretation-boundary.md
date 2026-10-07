# ADR 0001 — STR / LAMBDA Interpretation Boundary

## Status

Accepted.

## Decision

Promote the following architecture:

```text
SHAPES
    canonical structural ontology

    ↓ faithful structural transduction C

Tensor View
    representation mechanism

    ↓

STR
    Structural Tensor Representation

    ↓ interpretation-specific Λ_I

Interpretation I
    semantic domain D_I
```

with:

```text
Λ_I : STR -> D_I
```

for interpretations that choose the STR boundary.

The promoted architecture does **not** require every interpretation to use STR.

Direct interpretation from SHAPES remains admissible unless a specific
interpretation contract states otherwise.

---

## Context

The project previously promoted the separation:

```text
SHAPES
    structure

PETRA
    interpretation
```

with interpretation layers depending directly on SHAPES.

Subsequent research established a representation boundary between structural
ontology and interpretation semantics.

The relevant results are:

```text
SHAPES -> STR
    faithful for every finite SHAPES form

ADD / REMOVE over STR
    local structural-type quotient rewrite

LRPE
    factors through STR

Λ_LRPE : STR -> N+

LRPE = Λ_LRPE ∘ C
```

The LRPE result is particularly important because it demonstrates the boundary
with a maintained concrete interpretation rather than with a hypothetical
consumer.

---

## Promoted concepts

### SHAPES

SHAPES remains the sole structural ontology.

It owns:

- finite rooted non-plane structure;
- structural equality;
- child multiplicity;
- sibling non-order;
- intrinsic ADD;
- intrinsic REMOVE;
- intrinsic structural properties.

SHAPES does not own interpretation semantics.

### Tensor View

Tensor View is the promoted faithful structural transduction from SHAPES into
STR.

It is downstream of SHAPES.

It does not redefine SHAPES identity or semantics.

### STR

STR means:

```text
Structural Tensor Representation
```

For one finite SHAPES form, STR represents the finite quotient of distinct
rooted structural subform types through:

```text
(root, M)
```

where:

- `root` selects the root structural type;
- `M[i,j]` records the multiplicity of child structural type `j` under parent
  structural type `i`.

Local coordinates are representation metadata only.

The mathematical STR object is invariant under simultaneous coordinate
renaming.

STR contains structural information only.

It does not intrinsically contain:

- primes;
- exponent semantics;
- PETRA values;
- Collatz semantics;
- interpretation-specific numeric meaning;
- persistent occurrence identities;
- construction history.

### LAMBDA

LAMBDA is the promoted interpretation contract over STR.

For interpretation `I`:

```text
Λ_I : STR -> D_I
```

where `D_I` is interpretation-specific.

LAMBDA belongs only to the interpretation layer.

Therefore:

```text
SHAPES
    no Λ

Tensor View
    no Λ

STR
    no Λ

Interpretation I
    owns Λ_I
```

---

## PETRA / LRPE

PETRA remains a prime/exponent interpretation family over SHAPES.

The maintained LRPE policy has a proved STR factorization:

```text
C : SHAPES -> STR

Λ_LRPE : STR -> N+

LRPE = Λ_LRPE ∘ C
```

`Λ_LRPE` reconstructs the structural ordering required by LRPE directly from
the STR dependency DAG and evaluates the LRPE arithmetic without first
reconstructing a runtime `Shape`.

Therefore LRPE demonstrates that STR is sufficient for one maintained concrete
interpretation.

This does not mean:

```text
PETRA = STR
```

or:

```text
STR contains PETRA semantics.
```

PETRA semantics remain entirely above the STR boundary.

---

## Direct interpretation remains admissible

This decision does not establish:

```text
ALL INTERPRETATIONS MUST PASS THROUGH STR
```

The promoted architecture is:

```text
                         ┌── direct interpretation
                         │
SHAPES ──────────────────┤
                         │
                         └── Tensor View -> STR -> Λ_I -> D_I
```

The STR path is a promoted common representation boundary.

It is not yet a universal mandatory route.

A future decision may strengthen this requirement only after additional
evidence.

---

## Operational History

Operational History remains orthogonal to structural state and default LAMBDA
interpretation.

The default contract remains:

```text
Λ_I : STR -> D_I
```

not:

```text
Λ_I : (STR, OperationalHistory) -> D_I.
```

Different histories may converge to the same SHAPES form and therefore to the
same canonical STR and state-only interpretation result.

History-sensitive interpretation requires a separate explicit contract.

---

## ADD / REMOVE consequence

The promoted STR boundary is compatible with intrinsic SHAPES edit dynamics.

For legal ADD at parent depth `d`:

```text
|Q(S) △ Q(S')| <= 2(d + 1).
```

For legal REMOVE of a leaf at depth `d >= 1`:

```text
|Q(S) △ Q(S')| <= 2d.
```

The common quotient subgraph is preserved.

Canonical-coordinate churn is representational and is not structural delta.

Thus intrinsic edits induce local structural-type quotient rewrites in STR.

---

## Dependency direction

The promoted conceptual dependency is:

```text
interpretation semantics
        ↑
      LAMBDA
        ↑
       STR
        ↑
   Tensor View
        ↑
      SHAPES
```

Equivalently, implementation dependencies flow downward:

```text
interpretation
    -> STR / Tensor View
    -> SHAPES
```

when an interpretation chooses the STR path.

SHAPES never depends on STR, PETRA, or any interpretation.

STR never depends on PETRA or another semantic interpretation.

Sibling interpretations remain independent of one another.

---

## Evidence supporting the decision

The decision is supported by separately closed research gates:

```text
EXACT_CANONICAL_MATERIALIZATION_FAITHFULNESS=PROVED

ADD_REMOVE_EDIT_DYNAMICS_PROOF_GATE=PASS

LAMBDA_CONTRACT=FORMALIZED_AS_RESEARCH_CANDIDATE

PETRA_STR_FACTORIZATION_PROOF_GATE=PASS
```

In particular, LRPE establishes:

```text
LRPE_STR_FACTORIZATION=PROVED
LRPE_STR_COORDINATE_INVARIANCE=PROVED
SHAPE_DECODER_REQUIRED_BY_LAMBDA_LRPE=NO
PETRA_SPECIFIC_SEMANTICS_ADDED_TO_STR=NO
```

---

## Consequences

The following are now promoted architecture:

```text
TENSOR_VIEW=ARCHITECTURAL

STR=ARCHITECTURAL

LAMBDA=ARCHITECTURAL

LRPE_STR_FACTORIZATION=ACCEPTED_ARCHITECTURAL_RESULT
```

The following are explicitly not promoted by this decision:

```text
STR_MANDATORY_FOR_ALL_INTERPRETATIONS=NO

COLLATZ_SEMANTICS=PENDING_RESEARCH

OPERATIONAL_HISTORY_IN_DEFAULT_LAMBDA=NO

RUNTIME_STR_API=NOT_DEFINED

RUNTIME_PETRA_REFACTOR=NOT_AUTHORIZED_BY_THIS_DECISION
```

---

## Runtime boundary

This ADR changes architecture and documentation only.

It does not define:

- a Python STR class;
- Tensor View runtime APIs;
- LAMBDA protocol classes;
- serialization;
- caching;
- incremental STR maintenance;
- PETRA runtime migration;
- COLLATZ runtime behavior.

Those require separate design and implementation decisions.

---

## Final decision

```text
SHAPES_OWNS_ONTOLOGY=YES

TENSOR_VIEW_PROMOTED=YES

STR_PROMOTED=YES

LAMBDA_PROMOTED=YES

LRPE_FACTORIZATION_ACCEPTED=YES

STR_MANDATORY_FOR_ALL_INTERPRETATIONS=NO

DIRECT_INTERPRETATION_STILL_ALLOWED=YES

OPERATIONAL_HISTORY_SEPARATE=YES

RUNTIME_CHANGE=NONE
```
