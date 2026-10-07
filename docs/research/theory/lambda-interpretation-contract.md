# LAMBDA — Interpretation Contract over Structural Representation

## Status

Research architecture candidate.

Non-normative.

This note does not modify SHAPES semantics, PETRA semantics, runtime APIs, or
the currently promoted dependency graph in `docs/VISION.md`.

Any promotion of the architecture described here requires a separate explicit
architecture decision.

---

## 1. Motivation

The tensor-materialization research established that every finite SHAPES form
admits a faithful finite structural representation based on:

```text
(
    root vector,
    child-multiplicity matrix
)
```

over the finite quotient of distinct rooted structural subform types.

That representation is referred to here provisionally as:

```text
STR
=
Structural Tensor Representation
```

The important separation is:

```text
SHAPES
    defines form

Tensor View
    faithfully transduces form

STR
    carries the resulting mathematical structure

interpretation layer
    assigns meaning
```

The interpretation step therefore needs an explicit contract.

This note names that contract:

```text
LAMBDA
```

or symbolically:

```text
Λ
```

---

## 2. Core contract

Every interpretation `I` owns an explicit interpretation function:

```text
Λ_I : STR -> D_I
```

where:

```text
STR
```

is the shared structural representation and:

```text
D_I
```

is the semantic codomain chosen by interpretation `I`.

The codomain is not fixed globally.

Different interpretations may map the same STR into completely different
semantic domains.

Examples include:

```text
Λ_PETRA   : STR -> D_PETRA
Λ_COLLATZ : STR -> D_COLLATZ
Λ_X       : STR -> D_X
```

A concrete interpretation is responsible for defining:

1. its codomain;
2. the meaning it assigns to STR structure;
3. the mapping from STR into that codomain;
4. any interpretation-specific invariants or admissibility conditions.

LAMBDA specifies only that the mapping is explicit.

It does not prescribe what the mapping means.

---

## 3. Layer ownership

LAMBDA belongs only to the interpretation layer.

Therefore:

```text
SHAPES
    does not own Λ

Tensor View
    does not own Λ

STR
    does not own Λ

PETRA
    owns Λ_PETRA

COLLATZ
    owns Λ_COLLATZ

future interpretation I
    owns Λ_I
```

This boundary prevents interpretation-specific semantics from leaking downward
into the structural carrier or its faithful mathematical representation.

In particular, STR must not contain PETRA concepts merely because PETRA is one
consumer of STR.

STR therefore does not intrinsically know about:

- primes;
- exponents;
- recursive exponent towers;
- parity;
- Collatz dynamics;
- integer factorization;
- interpretation-specific numeric meaning.

Those meanings begin only when an interpretation applies its LAMBDA.

---

## 4. PETRA example

PETRA is one interpretation family.

Its LAMBDA may be written:

```text
Λ_PETRA : STR -> D_PETRA
```

where `D_PETRA` is PETRA's semantic domain.

PETRA may interpret structural properties through its own prime/exponent rules,
recursive tower rules, and related admissibility constraints.

Those rules belong to PETRA.

They are not properties of SHAPES or STR.

Conceptually:

```text
SHAPES
    ↓
Tensor View
    ↓
STR
    ↓ Λ_PETRA
PETRA semantic value
```

---

## 5. COLLATZ example

COLLATZ is a candidate sibling interpretation used to test architectural
agnosticism.

Its LAMBDA may be written:

```text
Λ_COLLATZ : STR -> D_COLLATZ
```

COLLATZ is not required to share PETRA's prime/exponent semantics.

Indeed, its value as an architectural test comes precisely from the possibility
that it assigns meaning according to a substantially different rule set.

For example, a COLLATZ interpretation may ultimately map STR into positive
integers and then study ordinary Collatz dynamics:

```text
STR
    ↓ Λ_COLLATZ
n in N+
    ↓
Collatz trajectory
```

The exact COLLATZ interpretation function is not defined by this note.

Only its architectural position is defined.

PETRA and COLLATZ are sibling interpretations.

Neither depends semantically on the other.

---

## 6. Interpretation independence

For sibling interpretations `I` and `J`:

```text
Λ_I : STR -> D_I

Λ_J : STR -> D_J
```

there is no requirement that:

```text
D_I = D_J
```

and no requirement that the two interpretation functions share internal
semantics.

Therefore:

```text
PETRA -X-> COLLATZ
COLLATZ -X-> PETRA
```

unless a future explicit architecture introduces a separate relationship.

Their commonality is only:

```text
both consume STR
both own an explicit LAMBDA
```

This gives the prospective architecture:

```text
                     SHAPES
                        ↓
                 faithful transduction
                        ↓
                   Tensor View
                        ↓
                       STR
                  /     |     \
                 /      |      \
                ↓       ↓       ↓
             PETRA   COLLATZ   Future X
                │       │        │
            Λ_PETRA Λ_COLLATZ   Λ_X
                │       │        │
                ↓       ↓        ↓
             D_PETRA D_COLLATZ  D_X
```

---

## 7. State versus operational history

LAMBDA interprets structural state.

By default:

```text
Λ_I : STR -> D_I
```

not:

```text
Λ_I : (STR, OperationalHistory) -> D_I
```

Operational History records how one operational instance reached its current
structural state.

It is provenance, not structural identity.

Therefore two operational instances may satisfy:

```text
History(A) != History(B)
```

while:

```text
Shape(A) = Shape(B).
```

Faithful canonical transduction then gives:

```text
STR(A) = STR(B).
```

For every state-only interpretation `I`:

```text
Λ_I(STR(A))
=
Λ_I(STR(B)).
```

Thus:

```text
same structural state
    => same canonical STR
    => same interpretation result

different operational history
    does not alter that result
```

This is intentional.

An interpretation that wishes to consume provenance must declare a different
contract explicitly rather than silently extending LAMBDA.

For example, a future history-sensitive interpretation might define:

```text
Ω_I : (STR, OperationalHistory) -> E_I
```

but that would not be the default LAMBDA contract established here.

---

## 8. Construction-history independence

Suppose two operation sequences produce structurally equal final forms:

```text
H_A : S0 -> ... -> S*

H_B : T0 -> ... -> T*
```

with:

```text
S* = T*
```

under SHAPES structural equality.

Then canonical structural representation gives:

```text
STR(S*) = STR(T*).
```

Therefore every deterministic state-only LAMBDA satisfies:

```text
Λ_I(STR(S*))
=
Λ_I(STR(T*)).
```

The interpretation result is consequently independent of construction history.

This does not erase history.

It preserves the separation:

```text
WHAT THE OBJECT IS
    structural state

HOW IT GOT THERE
    operational history

WHAT THE STATE MEANS TO I
    Λ_I(STR)
```

---

## 9. Agnosticism criterion

STR qualifies as a shared representation boundary only if sibling
interpretations can define genuinely different LAMBDA functions without
requiring interpretation-specific meaning to be embedded in STR.

A useful falsification criterion is therefore:

> If implementing a sibling interpretation requires STR to acquire PETRA-only
> concepts such as prime identity, exponent semantics, or PETRA tower meaning,
> the representation boundary is not sufficiently agnostic.

Likewise, COLLATZ-specific parity or trajectory semantics must not become STR
ontology merely because COLLATZ consumes STR.

The intended direction is:

```text
meaning flows upward

structure does not absorb meaning downward
```

---

## 10. Candidate architecture

The research candidate becomes:

```text
ONTOLOGY
    SHAPES

        ↓ faithful transduction

REPRESENTATION
    Tensor View
        ↓
    STR

        ↓ explicit interpretation

SEMANTICS
    Λ_PETRA
    Λ_COLLATZ
    Λ_X
    ...

PROVENANCE
    Operational History
```

Operational History is orthogonal to the default state interpretation path.

A more explicit view is:

```text
                   Operational History
                          │
                          │ produces / records
                          ▼
                        SHAPES
                          │
                          │ faithful transduction
                          ▼
                     Tensor View
                          │
                          ▼
                         STR
                    /     |     \
                   /      |      \
                  ▼       ▼       ▼
             Λ_PETRA  Λ_COLLATZ  Λ_X
                  │       │       │
                  ▼       ▼       ▼
                D_P     D_C      D_X
```

---

## 11. Architectural invariants

The candidate architecture requires:

```text
SHAPES_OWNS_STRUCTURE=YES

TENSOR_VIEW_OWNS_TRANSDUCTION=YES

STR_OWNS_INTERPRETATION_SEMANTICS=NO

LAMBDA_EXISTS_BELOW_INTERPRETATION_LAYER=NO

EACH_INTERPRETATION_OWNS_ITS_LAMBDA=YES

COMMON_LAMBDA_CODOMAIN_REQUIRED=NO

PETRA_SEMANTICS_IN_STR=NO

COLLATZ_SEMANTICS_IN_STR=NO

OPERATIONAL_HISTORY_IN_DEFAULT_LAMBDA=NO

CONSTRUCTION_HISTORY_AFFECTS_CANONICAL_STATE_INTERPRETATION=NO
```

---

## 12. Research verdict

The current research architecture candidate is:

```text
SHAPES
    ↓
Tensor View
    ↓
STR
    ↓
interpretation-specific LAMBDA
    ↓
semantic domain
```

with:

```text
Λ_I : STR -> D_I.
```

LAMBDA is the interpretation boundary.

It exists only at the interpretation layer.

PETRA and COLLATZ are the current concrete candidate siblings.

Operational History remains distinct from structural state and from default
interpretation semantics.

No promoted architecture change is made by this note.

```text
LAMBDA_CONTRACT=FORMALIZED_AS_RESEARCH_CANDIDATE

LAMBDA_LAYER=INTERPRETATION_ONLY

PETRA_LAMBDA=ALLOWED
COLLATZ_LAMBDA=ALLOWED

SHAPES_LAMBDA=NO
TENSOR_VIEW_LAMBDA=NO
STR_LAMBDA=NO

OPERATIONAL_HISTORY_SEPARATE=YES

VISION_PROMOTION=NOT_YET
NORMATIVE_CHANGE=NONE
RUNTIME_CHANGE=NONE
```

---

## 13. Next decision

Before promoting this architecture into `docs/VISION.md`, the research
programme should complete the current structural edit-dynamics work.

In particular:

```text
ADD / REMOVE
    ↓
ancestor-spine locality
    ↓
materialized-space edit dynamics
```

should be closed independently.

That separation prevents interpretation architecture and structural edit
dynamics from being conflated in one promotion decision.
