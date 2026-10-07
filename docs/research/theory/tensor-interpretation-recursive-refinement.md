# Tensor Interpretation via Recursive Structural Refinement

## Status

Research note.

This document records experimental evidence and a candidate theoretical
direction for a possible future interpretation layer over SHAPES.

It is **not**:

- SHAPES normative semantics;
- PETRA semantics;
- a production API contract;
- a roadmap commitment;
- a proof of the candidate faithfulness proposition;
- a commitment to a concrete tensor library or runtime representation.

The sole normative source for SHAPES semantics remains
`docs/reference/SPEC.md`.

Any future tensor interpretation would be a sibling interpretation layer over
SHAPES:

```text
PETRA ----------------\
                       \
future tensor layer ----> SHAPES
                       /
future interpretation -/
```

The dependency must remain:

```text
tensor interpretation -> SHAPES

SHAPES -X-> tensor interpretation
PETRA  -X-> tensor interpretation
```

unless a separate future architectural decision explicitly changes that
relationship.

---

## 1. Research question

The investigation began with a deliberately constrained question:

> Can SHAPES admit a tensor-valued interpretation without making tensor
> coordinates part of SHAPES ontology?

The investigation did **not** ask whether SHAPES itself is a tensor.

The architectural boundary was frozen throughout:

- SHAPES owns form;
- SHAPES structural equality remains authoritative;
- sibling order remains non-intrinsic;
- occurrence paths remain state-scoped selectors;
- no persistent occurrence identity is introduced;
- tensor coordinates do not define SHAPES identity;
- tensor machinery does not define `ADD` / `REMOVE` legality;
- SHAPES must not depend on the interpretation layer.

---

## 2. Controlled corpus

The probes enumerated finite SHAPES forms reachable through intrinsic `ADD`.

For the final refinement probe, the bounded corpus was:

```text
SIZE=1   SHAPES=1
SIZE=2   SHAPES=1
SIZE=3   SHAPES=2
SIZE=4   SHAPES=4
SIZE=5   SHAPES=9
SIZE=6   SHAPES=20
SIZE=7   SHAPES=48
SIZE=8   SHAPES=115
SIZE=9   SHAPES=286
SIZE=10  SHAPES=719
SIZE=11  SHAPES=1842

TOTAL_SHAPES=3047
MAX_HEIGHT=10
```

All probes were ephemeral.

They modified no repository files and left the worktree unchanged.

---

## 3. Probe sequence

### 3.1 Probe 0 — depth profile

Candidate:

```text
L(S)[d]
=
number of node occurrences at depth d
```

The candidate was invariant under structural equality but not faithful.

First collision:

```text
SIZE=5
TENSOR=(1, 2, 2)

LEFT_KEY=((())(()))
RIGHT_KEY=((()())())
```

Result:

```text
structurally invariant = yes
faithful                = no
```

This established that a tensor-like structural projection is admissible in
principle, but a depth histogram loses branching information.

---

### 3.2 Probe 1 — depth × arity

Candidate:

```text
T(S)[d,k]
=
number of node occurrences
at depth d
with exactly k children
```

It separated the Probe-0 collision.

Observed retention:

```text
SIZE=5  SHAPES=9   DISTINCT_TENSORS=9
SIZE=6  SHAPES=20  DISTINCT_TENSORS=20
SIZE=7  SHAPES=48  DISTINCT_TENSORS=47
SIZE=8  SHAPES=115 DISTINCT_TENSORS=109
SIZE=9  SHAPES=286 DISTINCT_TENSORS=258
```

First collision:

```text
SIZE=7
```

Result:

```text
more informative than Probe 0 = yes
faithful                      = no
```

Depth and local arity still lose parent-child correlation.

---

### 3.3 Probe 2 — edge arity incidence

Candidate:

```text
E(S)[d,a,b]
=
number of edges
from a parent at depth d with arity a
to a child with arity b
```

It separated the Probe-1 collision.

Observed retention:

```text
SIZE=7   SHAPES=48  DISTINCT_TENSORS=48
SIZE=8   SHAPES=115 DISTINCT_TENSORS=115
SIZE=9   SHAPES=286 DISTINCT_TENSORS=284
SIZE=10  SHAPES=719 DISTINCT_TENSORS=709
```

First collision:

```text
SIZE=9
```

Result:

```text
edge incidence adds information = yes
faithful                         = no
```

Local parent-child incidence still loses larger recursive composition.

---

### 3.4 Probe 3 — isolated length-2 path statistics

Candidate:

```text
P(S)[d,a,b,c]
=
number of length-2 paths

grandparent -> parent -> child

with arity sequence:

a -> b -> c
```

Taken **in isolation**, `P(S)` still collided at size 9.

This probe exposed a methodological issue:

replacing one projection with another does not test whether the new
information adds discrimination to the previous interpretation.

Therefore Probe 3 alone does not establish the incremental value of
length-2 path information.

---

### 3.5 Probe 3B — cumulative edge + path interpretation

Corrected cumulative candidate:

```text
C3(S)
=
(
    E(S),
    P(S)
)
```

The exact Probe-2 collision was frozen and retested.

Observed:

```text
EDGE_TENSOR_EQUAL=YES
PATH2_TENSOR_EQUAL=NO
CUMULATIVE_INTERPRETATION_EQUAL=NO
PROBE2_COLLISION_SEPARATED=YES
```

Retention:

```text
SIZE=9
SHAPES=286
EDGE_TENSORS=284
CUMULATIVE_TENSORS=285

SIZE=10
SHAPES=719
EDGE_TENSORS=709
CUMULATIVE_TENSORS=715

SIZE=11
SHAPES=1842
EDGE_TENSORS=1792
CUMULATIVE_TENSORS=1821
```

A different collision remained at size 9.

Result:

```text
length-2 information adds discrimination = yes
cumulative candidate faithful            = no
```

This established the methodological rule used afterward:

```text
F0
↓
(F0, F1)
↓
(F0, F1, F2)
↓
...
```

An enrichment must retain previous information rather than silently replace
it.

---

### 3.6 Probe 4 — sibling co-occurrence

The residual collision suggested loss of correlation between children sharing
the same parent.

New component:

```text
Q(S)[d,a,b,c]
=
number of unordered sibling pairs
with child arities b and c
under one parent of arity a
at depth d

with b <= c
```

Cumulative candidate:

```text
C4(S)
=
(
    E(S),
    P(S),
    Q(S)
)
```

The exact Probe-3B collision was separated:

```text
CUMULATIVE3_EQUAL=YES
SIBLING_COOCCURRENCE_EQUAL=NO
CUMULATIVE4_EQUAL=NO
PROBE3B_COLLISION_SEPARATED=YES
```

Retention:

```text
SIZE=9
SHAPES=286
CUMULATIVE4=286

SIZE=10
SHAPES=719
CUMULATIVE4=719

SIZE=11
SHAPES=1842
CUMULATIVE4=1840
```

The first residual collision moved to size 11.

Result:

```text
sibling correlation adds discrimination = yes
faithful through size 10 on this corpus  = yes
faithful in general                      = no
```

This was the point at which simply adding further local tensor statistics
became methodologically unattractive.

The remaining loss was no longer well described as one missing local
statistic.

It concerned recursive context.

---

## 4. Probe 5 — recursive structural refinement

Probe 5 replaced the growing collection of local statistics with a recursive
bottom-up structural refinement.

Define:

```text
c_0(v)
=
arity(v)
```

and recursively:

```text
c_(r+1)(v)
=
(
    arity(v),
    multiset{ c_r(child) }
)
```

For a SHAPES form `S`, define its radius-`r` root signature:

```text
R_r(S)
=
c_r(root(S))
```

The multiset is represented deterministically only for comparison.

That representation does not create intrinsic sibling order.

### 4.1 Structural invariance

Sibling permutation sanity checks passed:

```text
SIBLING_PERMUTATION_INVARIANCE_GATE=PASS
```

Thus the experimental refinement respected the SHAPES non-plane boundary.

---

## 5. Probe-4 collision under recursive refinement

The exact Probe-4 collision had:

```text
LEFT_HEIGHT=5
RIGHT_HEIGHT=5
```

Observed:

```text
RADIUS=0  equal
RADIUS=1  equal
RADIUS=2  equal
RADIUS=3  equal
RADIUS=4  different
RADIUS=5  different
...
```

Therefore:

```text
PROBE4_SEPARATION_RADIUS=4
```

The recursive refinement recovered the distinction that the cumulative local
statistics had lost.

---

## 6. Global refinement retention

Across all 3047 forms:

```text
radius  distinct signatures
------  -------------------
0       11
1       139
2       707
3       1607
4       2371
5       2806
6       2984
7       3036
8       3046
9       3047
10      3047
```

The first globally collision-free radius on this bounded corpus was:

```text
GLOBAL_FAITHFUL_RADIUS_ON_BOUND=9
```

The last collision occurred at radius 8 between forms of sizes 10 and 11.

Since:

```text
MAX_HEIGHT=10
```

the empirical threshold was:

```text
MAX_HEIGHT - 1 = 9
```

---

## 7. Adaptive height experiments

Two adaptive rules were tested.

### Radius equal to height

```text
R_height(S)(S)
```

No collision was found:

```text
HEIGHT_BOUND_SURVIVES_ON_BOUND=YES
```

### Radius equal to height minus one

Using:

```text
R_max(height(S)-1, 0)(S)
```

also produced no collision:

```text
HEIGHT_MINUS_ONE_BOUND_SURVIVES_ON_BOUND=YES
```

This is stronger and is the main theoretical lead produced by Probe 5.

---

## 8. Full recursive signature control

A full recursive signature was used as a control:

```text
F(v)
=
(
    arity(v),
    multiset{ F(child) }
)
```

No collision occurred on the corpus:

```text
FULL_SIGNATURE_COLLISION=NONE
FULL_SIGNATURE_FAITHFUL_ON_BOUND=YES
```

This is expected from the recursive SHAPES carrier, but the probe used it only
as an experimental control.

It does not redefine SHAPES structural equality.

---

## 9. Experimental conclusions

The probes support the following conclusions.

### E1 — tensor-like interpretations are architecturally admissible

A future interpretation can consume SHAPES structural information while
respecting:

```text
future interpretation -> SHAPES
```

and without importing tensor concepts into SHAPES ontology.

### E2 — local aggregate statistics are lossy

Every tested finite collection of local aggregate statistics eventually
collided:

```text
depth profile                    -> collision at size 5
depth × arity                    -> collision at size 7
edge arity incidence             -> collision at size 9
edge + length-2 path             -> collision at size 9
edge + path + sibling correlation -> collision at size 11
```

They can be useful projections.

They are not, from this evidence, suitable as the foundation of a faithful
structural encoding.

### E3 — cumulative enrichment matters

Adding information can strictly improve discrimination.

Replacing one projection with another does not establish that relation.

This distinction was exposed by Probe 3 and corrected by Probe 3B.

### E4 — recursive context is the important substrate

Recursive refinement recovered distinctions that increasingly rich local
statistics lost.

On the bounded corpus:

```text
R_9
```

was globally collision-free, exactly where:

```text
9 = MAX_HEIGHT - 1
```

### E5 — tensorization and faithful structural encoding are separate problems

The investigation now separates:

```text
1. faithful structural encoding

2. numerical / tensor materialization of that encoding
```

Probe 5 addresses the first problem.

It does **not** yet solve the second.

---

## 10. Candidate theoretical proposition

The empirical evidence suggests the following proposition.

Let `S` be a finite SHAPES form with height `h`.

Define:

```text
r(S)
=
max(h - 1, 0)
```

Candidate proposition:

> `R_r(S)(S)` is sufficient to determine `S` up to SHAPES structural
> equality.

Equivalently, the map:

```text
S
↦
R_max(height(S)-1,0)(S)
```

is conjectured to be faithful over finite SHAPES forms.

This is **not yet a promoted theorem**.

The bounded experiment:

```text
SIZE <= 11
TOTAL_SHAPES = 3047
MAX_HEIGHT = 10
```

found no counterexample.

---

## 11. Why height minus one may be sufficient

The candidate has a direct structural explanation.

At radius zero:

```text
c_0(v)
=
arity(v)
```

Therefore the terminal layer of a radius-`r` refinement does not merely state
that a node exists.

It still records that node's number of children.

For a form of height `h`, applying radius:

```text
h - 1
```

reaches nodes one level above the deepest leaves.

Their `c_0` values record their arities.

Since no node can exist below depth `h`, those children must be terminal.

Thus the final child multiplicities may already be determined without one
additional refinement round.

This is a proof intuition only.

It must be converted into a proper inductive argument before the proposition
is considered established.

---

## 12. Required proof gate

The next research step is not another larger tensor probe.

It is a proof/falsification gate for:

```text
Claim A

For every finite SHAPES form S of height h,

R_max(h-1,0)(S)

determines S uniquely up to SHAPES structural equality.
```

A suitable proof should be stated directly against the canonical recursive
carrier and finite child-multiset semantics.

The gate must distinguish:

```text
PROVED
FALSIFIED
PROOF_INCOMPLETE
```

If falsified, the counterexample becomes first-class research evidence.

If proved, only the structural refinement substrate is established.

Tensor materialization remains a separate research problem.

---

## 13. Possible future tensor interpretation

Only after the proof gate succeeds should the project investigate a pipeline
such as:

```text
SHAPES
    ↓
recursive structural refinement
    ↓
canonical structural states / types
    ↓
tensor materialization
```

Open representation questions include:

- fixed versus variable dimensionality;
- dense versus sparse representation;
- padding or masking;
- finite-support coordinate spaces;
- vocabulary construction for recursive structural types;
- whether tensorization should be faithful or intentionally lossy;
- edit locality under `ADD` / `REMOVE`;
- computational usefulness.

None of these choices is established by the current probes.

---

## 14. Architecture boundary

The investigation supports only this prospective architecture:

```text
                PETRA
                  ↓
                SHAPES
                  ↑
                  |
        future tensor interpretation
```

More explicitly:

```text
PETRA ----------------> SHAPES
tensor interpretation -> SHAPES
```

not:

```text
SHAPES -> tensor interpretation
```

as a dependency, and not:

```text
tensor coordinates -> SHAPES identity
```

The tensor interpretation, if ever promoted, must remain a consumer of the
structural core.

---

## 15. Current research verdict

```text
TENSOR INTERPRETATION ARCHITECTURALLY POSSIBLE
    YES

LOCAL TENSOR STATISTICS USEFUL
    YES

LOCAL AGGREGATE STATISTICS OBSERVED FAITHFUL IN GENERAL
    NO

RECURSIVE STRUCTURAL REFINEMENT PROMISING
    YES

R_(height-1) FAITHFULNESS PROVED
    NO

R_(height-1) FAITHFULNESS SURVIVES BOUNDED FALSIFICATION
    YES

TENSOR MATERIALIZATION ESTABLISHED
    NO

NEW SHAPES SEMANTICS
    NONE

NEW PETRA SEMANTICS
    NONE

NEXT GATE
    PROVE OR FALSIFY RECURSIVE-REFINEMENT FAITHFULNESS
```
