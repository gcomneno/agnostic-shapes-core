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
- a commitment to a concrete tensor library or runtime representation.

This note now contains a research-level proof of recursive-refinement
faithfulness derived from the existing SHAPES carrier and structural-equality
contract. The proof does not add or modify SHAPES semantics.

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

## 10. Recursive-refinement faithfulness theorem

The bounded evidence from Probe 5 suggested a stronger general result.

For every finite SHAPES form `S`, let:

```text
h(S)
=
height(S)
```

and define the adaptive radius:

```text
r(S)
=
max(h(S) - 1, 0)
```

The adaptive recursive-refinement signature is:

```text
A(S)
=
R_r(S)(S)
```

where:

```text
c_0(v)
=
arity(v)
```

and:

```text
c_(r+1)(v)
=
(
    arity(v),
    multiset{ c_r(child) }
)
```

with:

```text
R_r(S)
=
c_r(root(S))
```

### Theorem

For all finite SHAPES forms `S` and `T`:

```text
A(S) = A(T)
    => S = T
```

where equality on the right is canonical SHAPES structural equality.

Equivalently:

```text
S
↦
R_max(height(S)-1,0)(S)
```

is faithful over the complete finite SHAPES carrier.

This theorem is a result about a derived research encoding.

It does not redefine SHAPES structural equality.

---

## 11. Proof

The proof uses only the canonical SHAPES carrier:

```text
S ::= Node(M_f(S))
```

together with:

- finite rooted structure;
- finite child multisets;
- intrinsic child multiplicity;
- non-intrinsic sibling order;
- recursive structural equality.

### 11.1 Bounded-height faithfulness lemma

For every integer `r >= 0`:

> If finite SHAPES forms `S` and `T` both have height at most `r + 1`,
> then
>
> ```text
> R_r(S) = R_r(T)
>     => S = T.
> ```

#### Base case: `r = 0`

Assume:

```text
height(S) <= 1
height(T) <= 1
```

and:

```text
R_0(S) = R_0(T).
```

By definition:

```text
R_0(S) = arity(root(S))
R_0(T) = arity(root(T)).
```

Therefore the two roots have the same arity, say `n`.

Because both forms have height at most one, every child of either root is
zero-child and therefore has the unique SHAPES form:

```text
Z = Node(empty multiset).
```

Hence both forms are:

```text
Node({Z × n})
```

with the same multiplicity `n`.

Therefore:

```text
S = T.
```

The lemma holds for `r = 0`.

#### Inductive step

Assume the lemma holds for some `r >= 0`.

Let:

```text
height(S) <= r + 2
height(T) <= r + 2
```

and suppose:

```text
R_(r+1)(S) = R_(r+1)(T).
```

By the recursive definition of the refinement signature, equality implies both:

```text
arity(root(S))
=
arity(root(T))
```

and:

```text
multiset{
    R_r(U)
    : U is a child form of S
}
=
multiset{
    R_r(V)
    : V is a child form of T
}.
```

Every child form of `S` and `T` has height at most:

```text
r + 1.
```

Therefore the induction hypothesis applies to every matched pair of equal
radius-`r` child signatures.

For each such pair:

```text
R_r(U) = R_r(V)
    => U = V.
```

Consequently the two roots have equal finite multisets of child SHAPES forms,
including multiplicity.

By canonical SHAPES recursive structural equality:

```text
Node(M) = Node(N)
```

exactly when the child multisets can be matched bijectively while preserving
multiplicity and recursive structural equality.

Therefore:

```text
S = T.
```

The lemma follows for `r + 1`.

By induction, the bounded-height faithfulness lemma holds for every:

```text
r >= 0.
```

---

### 11.2 Recoverability of height from the adaptive signature

The adaptive map uses a radius chosen from the input form itself.

Therefore faithfulness also requires ruling out collisions between forms of
different heights.

The adaptive signature carries enough information to recover its source
height.

#### Height zero

If:

```text
height(S) = 0
```

then `S = Z`, the root has arity zero, and:

```text
A(S) = R_0(S) = 0.
```

#### Height one

If:

```text
height(S) = 1
```

then the root has at least one child and:

```text
A(S) = R_0(S) = arity(root(S)) > 0.
```

Thus heights zero and one are already distinguished by the integer adaptive
signature.

#### Height at least two

If:

```text
height(S) = h >= 2,
```

then:

```text
A(S) = R_(h-1)(S).
```

The signature is recursively nested.

Because `S` has height exactly `h`, at least one root-to-leaf path reaches
depth `h`.

Along that path, recursive refinement therefore reaches nesting depth exactly:

```text
h - 1.
```

It cannot reach greater nesting depth because no occurrence exists below
depth `h`.

Hence the recursive nesting depth of `A(S)` is exactly:

```text
h - 1.
```

So the source height is recoverable from the adaptive signature:

```text
A(S) = 0
    => height(S) = 0

A(S) is a positive integer
    => height(S) = 1

A(S) has recursive nesting depth d >= 1
    => height(S) = d + 1.
```

Therefore:

```text
A(S) = A(T)
    => height(S) = height(T).
```

---

### 11.3 Adaptive faithfulness

Assume:

```text
A(S) = A(T).
```

By height recoverability:

```text
height(S) = height(T) = h.
```

If `h = 0`, both forms are `Z`, so:

```text
S = T.
```

If `h >= 1`, define:

```text
r = h - 1.
```

Then:

```text
A(S) = R_r(S)
A(T) = R_r(T)
```

and both forms have height:

```text
h = r + 1.
```

The bounded-height faithfulness lemma therefore gives:

```text
R_r(S) = R_r(T)
    => S = T.
```

Hence:

```text
A(S) = A(T)
    => S = T.
```

This proves the theorem.

```text
QED
```

---

## 12. Proof gate result

The proof/falsification gate is closed as:

```text
RECURSIVE_REFINEMENT_WELL_DEFINED=PROVED
BOUNDED_HEIGHT_FAITHFULNESS=PROVED
ADAPTIVE_HEIGHT_RECOVERABILITY=PROVED
R_(height-1)_FAITHFULNESS=PROVED

COUNTEREXAMPLE=NONE
PROOF_GATE=PASS
```

The Probe-5 bounded result is now explained as a finite instance of the
theorem.

For that corpus:

```text
MAX_HEIGHT=10
```

and the first globally collision-free fixed radius was:

```text
r=9.
```

This matches:

```text
MAX_HEIGHT - 1 = 9.
```

The proof establishes only the faithful recursive structural substrate.

Tensor materialization remains a separate research problem.

---

## 13. Possible future tensor interpretation

With recursive-refinement faithfulness established, the next research problem
is tensor materialization of the faithful structural substrate.

A candidate pipeline is:

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

RECURSIVE STRUCTURAL REFINEMENT FAITHFUL
    PROVED

R_(height-1) FAITHFULNESS PROVED
    YES

R_(height-1) FAITHFULNESS SURVIVES BOUNDED FALSIFICATION
    YES

TENSOR MATERIALIZATION ESTABLISHED
    NO

NEW SHAPES SEMANTICS
    NONE

NEW PETRA SEMANTICS
    NONE

NEXT GATE
    INVESTIGATE TENSOR MATERIALIZATION
```
