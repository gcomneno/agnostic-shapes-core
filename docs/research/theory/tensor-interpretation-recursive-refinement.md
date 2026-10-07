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

## 14. Tensor Materialization Probe 0

With recursive-refinement faithfulness established, the next question was
whether one finite SHAPES form could be converted into a self-contained finite
numeric representation without retaining recursive signatures as hidden
decoder metadata.

For a finite form `S`, let `Q(S)` be the finite set of distinct rooted SHAPES
subforms that occur in `S`.

A local coordinate assignment:

```text
pi : Q(S) -> {0, ..., k-1}
```

with:

```text
k = |Q(S)|
```

was used to construct:

```text
T(S)
=
(
    root,
    M
)
```

where:

```text
root[i] = 1
```

exactly when coordinate `i` denotes the root structural type `S`, and:

```text
M[i,j]
=
multiplicity of child type j
under parent type i.
```

The coordinates are local representation indices only.

They are not:

- SHAPES identity;
- occurrence identity;
- sibling order;
- globally meaningful structural type IDs.

### 14.1 Controlled experiment

The ephemeral Probe 0 enumerated every SHAPES form reachable through intrinsic
`ADD` up to size 11:

```text
SIZE=1      1
SIZE=2      1
SIZE=3      2
SIZE=4      4
SIZE=5      9
SIZE=6      20
SIZE=7      48
SIZE=8      115
SIZE=9      286
SIZE=10     719
SIZE=11     1842

TOTAL_SHAPES=3047
```

For every form, the probe:

```text
source SHAPE
    ↓
collect local structural types
    ↓
assign deterministic local coordinates
    ↓
materialize (root, M)
    ↓
discard source SHAPE and structural-type vocabulary
    ↓
decode using only (root, M)
    ↓
compare with source by SHAPES structural equality
```

Observed:

```text
ROUNDTRIP_OK=3047
TOTAL_SHAPES=3047
DISTINCT_MATERIALIZATIONS=3047
COLLISION_COUNT=0
LOCAL_TYPE_REDUNDANCY_COUNT=0
UNREACHABLE_TYPE_COORDINATE_COUNT=0
MAX_LOCAL_VOCABULARY=11
MAX_MATRIX_DIMENSION=11
```

All experimental gates passed:

```text
ROUNDTRIP_GATE=PASS
COLLISION_GATE=PASS
LOCAL_TYPE_ROW_UNIQUENESS_GATE=PASS
TYPE_REACHABILITY_GATE=PASS
```

The decoder required only:

```text
(root, M)
```

and did not retain the recursive structural signatures or source `Shape`
values.

The bounded experimental verdict was:

```text
TENSOR_MATERIALIZATION_PROBE_0
=
MATERIALIZATION_FAITHFUL_ON_BOUND
```

The probe modified no repository state.

---

## 15. Tensor materialization faithfulness theorem

Probe 0 suggests a general result over the complete finite SHAPES carrier.

Let `S` be any finite SHAPES form.

Define `Q(S)` as the set of distinct structural types among all rooted subforms
occurring in `S`.

Choose a bijective local coordinate assignment:

```text
pi : Q(S) -> {0, ..., k-1}
```

and define:

```text
root_pi(S)[pi(S)] = 1
```

with every other root coordinate zero.

Define the child-multiplicity matrix:

```text
M_pi(S)[pi(U), pi(V)]
=
multiplicity of V
in the child multiset of U.
```

The coordinate-labelled materialization is:

```text
T_pi(S)
=
(
    root_pi(S),
    M_pi(S)
)
```

### Theorem

For every finite SHAPES form `S`, `T_pi(S)` is a finite self-contained
representation from which `S` can be reconstructed uniquely up to SHAPES
structural equality.

Consequently, the materialization is faithful modulo simultaneous renaming of
its local type coordinates.

If the local coordinate assignment is chosen by a deterministic canonical
policy derived solely from structural type, the resulting canonical
materialization is an injective deterministic encoding of finite SHAPES forms.

This theorem concerns a derived interpretation representation.

It does not redefine SHAPES structural equality or ontology.

---

### 15.1 Finite structural-type quotient

Every finite SHAPES form has finitely many node occurrences.

Every rooted subform occurring in `S` is rooted at some occurrence of `S`.

Therefore the number of distinct structural subform types satisfies:

```text
1 <= |Q(S)| <= size(S).
```

Hence `Q(S)` is finite.

Therefore:

```text
root_pi(S)
```

is a finite vector and:

```text
M_pi(S)
```

is a finite square matrix.

Thus every finite SHAPES form admits a finite materialization.

```text
FINITE_TYPE_QUOTIENT=PROVED
FINITE_MATERIALIZATION=PROVED
```

---

### 15.2 Acyclicity of structural-type dependency

Suppose structural type `V` occurs as an immediate child of structural type
`U`.

Then:

```text
height(V) < height(U).
```

Indeed, every root-to-leaf path in `V` becomes one level deeper when viewed
from the root of `U`.

Therefore every directed dependency:

```text
U -> V
```

strictly decreases height.

A directed cycle would require:

```text
height(U)
>
...
>
height(U),
```

which is impossible.

Hence the structural-type dependency graph represented by the non-zero entries
of `M_pi(S)` is acyclic.

It therefore admits a bottom-up topological reconstruction order.

```text
TYPE_DEPENDENCY_ACYCLIC=PROVED
```

---

### 15.3 Decoder definition and termination

Given only:

```text
(root, M),
```

define a decoder on type coordinates recursively.

For coordinate `i`, let:

```text
D(i)
=
Node(
    multiset {
        D(j) repeated M[i,j] times
        for every j
    }
)
```

Rows with no outgoing multiplicities decode immediately as:

```text
Node(empty multiset)
=
Z.
```

Because the dependency graph is finite and acyclic, recursive decoding always
reaches zero-child rows.

Therefore decoding terminates.

The one-hot root vector selects one coordinate `r`, and the decoded form is:

```text
Decode(root, M)
=
D(r).
```

No structural-type vocabulary is required by the decoder.

```text
DECODER_TERMINATES=PROVED
DECODER_REQUIRES_STRUCTURAL_VOCABULARY=NO
```

---

### 15.4 Decoder correctness

We prove that every coordinate reconstructs its corresponding structural type.

Let coordinate `pi(U)` represent structural type `U`.

Proceed by induction on:

```text
height(U).
```

#### Base case

If:

```text
height(U) = 0,
```

then `U` has no children.

Its matrix row contains only zeroes.

Therefore:

```text
D(pi(U))
=
Node(empty multiset)
=
Z
=
U.
```

#### Inductive step

Assume every structural type of height strictly less than `h` is reconstructed
correctly.

Let:

```text
height(U) = h > 0.
```

Every immediate child type `V` of `U` has:

```text
height(V) < h.
```

By the induction hypothesis:

```text
D(pi(V)) = V.
```

The row:

```text
M_pi(S)[pi(U), *]
```

contains exactly the multiplicity with which each child structural type occurs
under `U`.

Therefore the decoder constructs exactly:

```text
Node(
    child multiset of U
).
```

By canonical SHAPES recursive structural equality:

```text
D(pi(U)) = U.
```

The induction therefore holds for every type in `Q(S)`.

In particular, the root vector selects `pi(S)`, so:

```text
Decode(T_pi(S))
=
S.
```

Hence:

```text
ROUNDTRIP_FOR_ALL_FINITE_SHAPES=PROVED
DECODER_CORRECTNESS=PROVED
```

---

### 15.5 Faithfulness modulo local-coordinate renaming

The integer coordinate attached to one local structural type has no intrinsic
meaning.

Let:

```text
sigma
```

be any permutation of the `k` local coordinates.

Applying that renaming simultaneously to:

```text
root
```

and both axes of:

```text
M
```

does not change the represented rooted multiplicity structure.

In matrix notation, if `P` is the corresponding permutation matrix:

```text
root' = P root

M' = P M P^-1.
```

Therefore the mathematically natural materialization object is the equivalence
class:

```text
[(root, M)]
```

under simultaneous local-coordinate renaming.

Since every representative decodes to the same SHAPES form:

```text
[(root, M)]
    ↦
S
```

is well-defined.

If two finite SHAPES forms have the same materialization class, decoding that
class yields both forms.

Therefore:

```text
[T(S)] = [T(U)]
    => S = U.
```

Hence:

```text
FAITHFUL_UP_TO_LOCAL_COORDINATE_RENAMING=PROVED
```

No global type identifiers are required.

---

### 15.6 Canonical local coordinate assignment

For exact deterministic materialization rather than equivalence only, choose a
fixed total ordering of structural types derived solely from a faithful
structural signature.

One admissible policy is the policy used in Probe 0:

```text
(
    height(type),
    full_recursive_structural_signature(type)
)
```

with deterministic total ordering of the resulting structural signatures.

Because both height and the recursive signature depend only on SHAPES
structure, structurally equal types receive the same ordering relation
independently of:

- occurrence identity;
- construction history;
- sibling order;
- object allocation;
- traversal accidents.

For one finite `S`, ordering all members of `Q(S)` by that policy therefore
induces a unique local coordinate assignment:

```text
pi_canonical(S).
```

This produces:

```text
C(S)
=
T_pi_canonical(S)(S).
```

If:

```text
S = U,
```

then the two forms have the same finite set of structural subform types and the
same canonical ordering.

Therefore:

```text
C(S) = C(U).
```

Conversely, if:

```text
C(S) = C(U),
```

then the common numerical representation decodes to one unique SHAPES form.

By decoder correctness:

```text
S = U.
```

Thus:

```text
S = U
iff
C(S) = C(U).
```

So the canonical materialization is an injective deterministic representation
of finite SHAPES forms.

This establishes exact equality of the mathematical vector/matrix pair.

It does **not** claim byte-for-byte serialization identity, because no tensor
serialization format is specified by this research result.

```text
CANONICAL_COORDINATE_ASSIGNMENT=PROVED
EXACT_CANONICAL_MATERIALIZATION_FAITHFULNESS=PROVED
BYTE_SERIALIZATION_CONTRACT=NONE
```

---

### 15.7 Row uniqueness and reachability corollaries

Two distinct structural types in the same local vocabulary cannot have equal
matrix rows.

If two rows were equal, they would specify equal child-type multisets with
equal multiplicities.

By SHAPES recursive structural equality, the corresponding parent structural
types would then be equal.

Therefore:

```text
LOCAL_TYPE_ROW_UNIQUENESS=PROVED
```

Every type in `Q(S)` occurs as a rooted subform somewhere inside `S`.

Following the ancestor chain from that occurrence to the root gives a path in
the type-dependency graph from the root type to that structural type.

Therefore every materialized coordinate is reachable from the root coordinate:

```text
TYPE_REACHABILITY=PROVED
```

These general results explain the corresponding Probe-0 observations:

```text
LOCAL_TYPE_REDUNDANCY_COUNT=0
UNREACHABLE_TYPE_COORDINATE_COUNT=0.
```

---

## 16. Tensor materialization proof gate result

The proof gate is closed as:

```text
FINITE_TYPE_QUOTIENT=PROVED
FINITE_MATERIALIZATION=PROVED

TYPE_DEPENDENCY_ACYCLIC=PROVED

DECODER_TERMINATES=PROVED
DECODER_CORRECTNESS=PROVED
ROUNDTRIP_FOR_ALL_FINITE_SHAPES=PROVED

FAITHFUL_UP_TO_LOCAL_COORDINATE_RENAMING=PROVED

CANONICAL_COORDINATE_ASSIGNMENT=PROVED
EXACT_CANONICAL_MATERIALIZATION_FAITHFULNESS=PROVED

LOCAL_TYPE_ROW_UNIQUENESS=PROVED
TYPE_REACHABILITY=PROVED

GLOBAL_TYPE_IDS_REQUIRED=NO
PERSISTENT_OCCURRENCE_IDENTITY_REQUIRED=NO
SIBLING_ORDER_REQUIRED=NO

BYTE_SERIALIZATION_CONTRACT=NONE

NEW_SHAPES_SEMANTICS=NONE
NEW_PETRA_SEMANTICS=NONE
RUNTIME_CHANGE=NONE

TENSOR_MATERIALIZATION_PROOF_GATE=PASS
```

The resulting research pipeline is now:

```text
SHAPES
    ↓
recursive structural refinement
    FAITHFUL — PROVED
    ↓
finite structural-type quotient
    ↓
(root vector, child-multiplicity matrix)
    FAITHFUL — PROVED
```

The matrix does not store node occurrences.

It stores the recursive construction rules of the distinct structural types
present in one finite SHAPES form.

The next research question is therefore no longer whether a faithful tensor
materialization exists.

It is:

> How do intrinsic `ADD` and `REMOVE` edits transform this materialization?

In particular, future work may investigate whether such changes are:

- local;
- sparse;
- bounded in affected tensor support;
- compositional;
- expressible through useful algebraic update rules.

No such edit-dynamics result is established here.

---

## 17. ADD / REMOVE materialized-space Probe 0

After establishing faithful tensor materialization, the next research question
was how intrinsic SHAPES edits transform the finite structural-type quotient.

The probe separated two notions that must not be conflated:

```text
STRUCTURAL / QUOTIENT DELTA
    which structural types actually appear or disappear

CANONICAL-COORDINATE CHURN
    which surviving structural types merely receive different
    local numeric coordinates after canonical reindexing
```

The hypothesis was:

> An intrinsic `ADD` or `REMOVE` changes structurally only the ancestor spine
> from the edited parent through the root.

### 17.1 Controlled corpus

The probe reused the complete bounded corpus through size 11:

```text
SIZE=1      1
SIZE=2      1
SIZE=3      2
SIZE=4      4
SIZE=5      9
SIZE=6      20
SIZE=7      48
SIZE=8      115
SIZE=9      286
SIZE=10     719
SIZE=11     1842

TOTAL_SHAPES=3047
```

It then examined:

```text
ADD:
    every legal ADD from every form of size <= 10

REMOVE:
    every legal removal of every non-root leaf
    from every form of size <= 11
```

Observed:

```text
ADD_TRANSITIONS=11210
MAX_ADD_AFFECTED_SPINE_TYPES=10
MAX_ADD_REMOVED_TYPES=9
MAX_ADD_ADDED_TYPES=9
MAX_ADD_TYPE_SYMMETRIC_DIFFERENCE=18
MAX_ADD_CANONICAL_COORDINATE_CHURN=6

REMOVE_TRANSITIONS=14594
MAX_REMOVE_AFFECTED_SPINE_TYPES=10
MAX_REMOVE_REMOVED_TYPES=9
MAX_REMOVE_ADDED_TYPES=9
MAX_REMOVE_TYPE_SYMMETRIC_DIFFERENCE=18
MAX_REMOVE_CANONICAL_COORDINATE_CHURN=6
```

Across all:

```text
25804
```

tested legal transitions:

```text
OFF_SPINE_STRUCTURAL_CHANGE=NONE
ANCESTOR_SPINE_LOCALITY=SUPPORTED_ON_BOUND
FIRST_FAILURE=NONE
```

Both locality gates passed.

---

### 17.2 Coordinate churn observation

The probe deliberately measured canonical coordinate churn separately from
structural-type change.

The worst observed ADD case had:

```text
WORST_ADD_SPINE_LENGTH=2
WORST_ADD_COORDINATE_CHURN=6/7
```

and the inverse REMOVE case had:

```text
WORST_REMOVE_SPINE_LENGTH=2
WORST_REMOVE_COORDINATE_CHURN=6/7
```

Thus an edit affecting a structurally short ancestor spine can cause many
surviving structural types to receive new canonical coordinate numbers.

This does not imply equally broad structural change.

Canonical coordinates are representation indices.

They are not structural identity.

The bounded experimental conclusion was therefore:

```text
CANONICAL_COORDINATE_CHURN_IS_REPRESENTATIONAL=YES
```

---

## 18. Ancestor-spine locality theorem

Let:

```text
S
```

be a finite SHAPES form.

Let:

```text
Q(S)
```

denote its finite set of distinct rooted structural subform types.

We study separately intrinsic `ADD` and intrinsic `REMOVE`.

The result is stated over structural types, not persistent node identities.

Occurrence paths remain operation-local selectors only.

---

### 18.1 ADD reconstruction spine

Consider a legal:

```text
ADD(S, p)
```

where `p` selects a parent occurrence at depth:

```text
d.
```

Let the selected rooted subform be:

```text
U_d.
```

Let its ancestors toward the root be:

```text
U_d,
U_(d-1),
...
U_0
```

with:

```text
U_0 = S.
```

Intrinsic ADD first constructs:

```text
U'_d
=
Node(
    children(U_d) multiset-union {Z}
)
```

and then rebuilds each ancestor by replacing exactly the selected child
incidence with its rebuilt successor:

```text
U'_(d-1),
...
U'_0.
```

The target form is:

```text
S' = U'_0.
```

Therefore exactly:

```text
d + 1
```

ancestor occurrences are rebuilt.

No other pre-existing occurrence is structurally edited.

Its position in a canonical tuple may change because sibling order is
representational, but its rooted SHAPES value remains unchanged.

Hence:

```text
ADD_ANCESTOR_SPINE_RECONSTRUCTION=PROVED
```

---

### 18.2 ADD off-spine preservation

Every old occurrence outside the rebuilt ancestor spine lies either:

1. below the selected parent as an unchanged pre-existing descendant; or
2. inside an untouched sibling subtree of some rebuilt ancestor.

Intrinsic ADD changes neither such rooted subform.

Therefore every old structural type that has an occurrence outside the old
ancestor spine still occurs in the target.

Consequently:

```text
Q(S) \ Q(S')
    ⊆
OldSpineTypes.
```

Likewise, every genuinely new rooted structural type in the target must arise
from one of the rebuilt ancestor occurrences:

```text
Q(S') \ Q(S)
    ⊆
NewSpineTypes.
```

Thus:

```text
ADD_OFF_SPINE_TYPE_PRESERVATION=PROVED
```

---

### 18.3 ADD quotient-delta bound

The old ADD spine contains:

```text
d + 1
```

occurrences.

Therefore it contains at most:

```text
d + 1
```

distinct structural types.

The new spine has the same occurrence count and therefore also at most:

```text
d + 1
```

distinct structural types.

Since all disappearing types come from the old spine and all appearing types
come from the new spine:

```text
|Q(S) \ Q(S')| <= d + 1

|Q(S') \ Q(S)| <= d + 1.
```

Hence:

```text
|Q(S) △ Q(S')|
<=
2(d + 1).
```

The bound is on distinct quotient types.

Repeated equal structural types along or outside the spine may make the actual
delta strictly smaller.

Therefore:

```text
ADD_QUOTIENT_DELTA_BOUND=PROVED
```

---

### 18.4 REMOVE reconstruction spine

Consider a legal:

```text
REMOVE(S, p)
```

where `p` selects a non-root zero-child occurrence at depth:

```text
d >= 1.
```

The removed leaf itself is not rebuilt.

Its parent, at depth:

```text
d - 1,
```

is rebuilt with one selected zero-child incidence removed.

Every ancestor from that parent through the root is then rebuilt.

Therefore the rebuilt occurrence spine contains exactly:

```text
d
```

occurrences.

No other surviving occurrence is structurally edited.

Hence:

```text
REMOVE_ANCESTOR_SPINE_RECONSTRUCTION=PROVED
```

---

### 18.5 REMOVE off-spine preservation

Every surviving occurrence outside the rebuilt ancestor spine retains exactly
the same rooted SHAPES value.

The deleted occurrence has type:

```text
Z.
```

But every finite rooted tree has at least one zero-child occurrence.

Since REMOVE cannot delete the root, its finite target still contains a
zero-child occurrence.

Therefore:

```text
Z
```

does not disappear from the structural-type quotient merely because one leaf
occurrence was removed.

Every structural type that actually disappears must therefore be one of the
old rebuilt ancestor types:

```text
Q(S) \ Q(S')
    ⊆
OldAncestorSpineTypes.
```

Every new type must be one of the rebuilt target ancestor types:

```text
Q(S') \ Q(S)
    ⊆
NewAncestorSpineTypes.
```

Thus:

```text
REMOVE_OFF_SPINE_TYPE_PRESERVATION=PROVED
```

---

### 18.6 REMOVE quotient-delta bound

The old and new rebuilt ancestor spines each contain:

```text
d
```

occurrences and therefore at most:

```text
d
```

distinct structural types.

Hence:

```text
|Q(S) \ Q(S')| <= d

|Q(S') \ Q(S)| <= d.
```

Therefore:

```text
|Q(S) △ Q(S')|
<=
2d.
```

Again, equality is not required because repeated structural types can reduce
the distinct quotient delta.

Thus:

```text
REMOVE_QUOTIENT_DELTA_BOUND=PROVED
```

---

### 18.7 Preservation of surviving quotient rules

Let:

```text
U ∈ Q(S) ∩ Q(S').
```

Since `U` is the same SHAPES structural type in both states, its intrinsic
child multiset is identical in both states.

If structural type `V` is a child type of `U`, then an occurrence of `U`
contains an occurrence of `V`.

Therefore, because `U` occurs in both `S` and `S'`:

```text
V ∈ Q(S) ∩ Q(S').
```

Thus no surviving structural type can depend on a quotient type that exists
only on one side of the transition.

Its complete multiplicity rule is preserved.

Therefore the quotient substructure carried by:

```text
Q(S) ∩ Q(S')
```

is identical before and after the edit.

Only old spine types may be deleted and only new spine types may be inserted.

Hence intrinsic ADD and REMOVE induce a:

```text
LOCAL STRUCTURAL-TYPE QUOTIENT REWRITE
```

modulo local-coordinate renaming.

Therefore:

```text
SURVIVING_QUOTIENT_RULES_PRESERVED=PROVED
COMMON_QUOTIENT_SUBGRAPH_PRESERVED=PROVED
LOCAL_QUOTIENT_REWRITE=PROVED
```

---

### 18.8 Structural delta versus canonical reindexing

Canonical tensor materialization assigns local coordinates by ordering the
current finite type vocabulary.

An ADD or REMOVE may insert or remove structural types from that ordered
vocabulary.

Therefore a surviving structural type can receive a different numeric
coordinate even though:

- the structural type itself is unchanged;
- its child-multiplicity rule is unchanged;
- its role in the common quotient subgraph is unchanged.

Consequently:

```text
canonical coordinate index
```

is not a valid intrinsic measure of edit locality.

The correct structural object is the quotient representation modulo
simultaneous coordinate renaming.

Canonical matrix churn must therefore be separated from structural quotient
delta.

```text
CANONICAL_REINDEXING_IS_REPRESENTATIONAL=PROVED
COORDINATE_CHURN_IS_NOT_STRUCTURAL_DELTA=PROVED
```

No general bound on canonical-coordinate churn is claimed here.

---

### 18.9 Materialized-space edit theorem

Combining the preceding results:

For every legal intrinsic ADD:

```text
SHAPES edit
    ↓
rebuild one ancestor spine
    ↓
delete at most d+1 old quotient types
    ↓
insert at most d+1 new quotient types
    ↓
preserve every surviving quotient construction rule
```

and:

```text
|Q(S) △ Q(S')|
<=
2(d+1).
```

For every legal intrinsic REMOVE of a leaf at depth `d >= 1`:

```text
SHAPES edit
    ↓
rebuild parent-to-root ancestor spine
    ↓
delete at most d old quotient types
    ↓
insert at most d new quotient types
    ↓
preserve every surviving quotient construction rule
```

and:

```text
|Q(S) △ Q(S')|
<=
2d.
```

Therefore intrinsic SHAPES edits are structurally local in the faithful
materialized representation when locality is measured over structural types
rather than canonical coordinate numbers.

This proves:

```text
ADD_MATERIALIZED_LOCALITY=PROVED
REMOVE_MATERIALIZED_LOCALITY=PROVED
MATERIALIZED_EDIT_LOCALITY=PROVED
```

---

## 19. ADD / REMOVE edit-dynamics proof gate result

The edit-dynamics gate is closed as:

```text
ADD_ANCESTOR_SPINE_RECONSTRUCTION=PROVED
REMOVE_ANCESTOR_SPINE_RECONSTRUCTION=PROVED

ADD_OFF_SPINE_TYPE_PRESERVATION=PROVED
REMOVE_OFF_SPINE_TYPE_PRESERVATION=PROVED

ADD_QUOTIENT_DELTA_BOUND=PROVED
REMOVE_QUOTIENT_DELTA_BOUND=PROVED

SURVIVING_QUOTIENT_RULES_PRESERVED=PROVED
COMMON_QUOTIENT_SUBGRAPH_PRESERVED=PROVED
LOCAL_QUOTIENT_REWRITE=PROVED

CANONICAL_REINDEXING_IS_REPRESENTATIONAL=PROVED
COORDINATE_CHURN_IS_NOT_STRUCTURAL_DELTA=PROVED

ADD_MATERIALIZED_LOCALITY=PROVED
REMOVE_MATERIALIZED_LOCALITY=PROVED
MATERIALIZED_EDIT_LOCALITY=PROVED

NEW_SHAPES_SEMANTICS=NONE
NEW_PETRA_SEMANTICS=NONE
RUNTIME_CHANGE=NONE

ADD_REMOVE_EDIT_DYNAMICS_PROOF_GATE=PASS
```

The resulting research chain is now:

```text
SHAPES
    ↓
faithful recursive structural refinement
    ↓
faithful finite tensor materialization
    ↓
local structural-type quotient rewrite under ADD / REMOVE
```

This closes the question raised after tensor materialization:

> Do intrinsic SHAPES edits remain local in materialized structural space?

Answer:

```text
YES
```

provided locality is evaluated structurally modulo coordinate renaming rather
than by raw canonical matrix indices.

The next research question is no longer ADD / REMOVE locality.

A future tranche may investigate incremental maintenance algorithms or
architecture promotion, but neither is established by this proof.

---

## 20. Architecture boundary

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

## 21. Current research verdict

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

TENSOR MATERIALIZATION FAITHFULNESS PROVED
    YES

FINITE SELF-CONTAINED ROOT + MULTIPLICITY MATRIX REPRESENTATION
    YES

GLOBAL TYPE IDS REQUIRED
    NO

BYTE SERIALIZATION CONTRACT
    NONE

NEW SHAPES SEMANTICS
    NONE

NEW PETRA SEMANTICS
    NONE

ADD / REMOVE MATERIALIZED LOCALITY
    PROVED

LOCAL QUOTIENT REWRITE
    PROVED

CANONICAL COORDINATE CHURN
    REPRESENTATIONAL, NOT STRUCTURAL

ADD / REMOVE EDIT-DYNAMICS GATE
    CLOSED

NEXT GATE
    ARCHITECTURE PROMOTION DECISION OR INCREMENTAL STR MAINTENANCE
```
