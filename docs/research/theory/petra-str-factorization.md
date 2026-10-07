# PETRA / STR Factorization — LRPE

## Status

Research result.

Non-normative.

This note proves that the currently maintained LRPE interpretation can be
evaluated through the faithful Structural Tensor Representation without
requiring a reconstructed runtime `Shape`.

It does not modify:

- SHAPES semantics;
- PETRA normative semantics;
- LRPE runtime behavior;
- public APIs;
- `docs/VISION.md`;
- `docs/reference/PETRA.md`.

Any architecture promotion remains a separate explicit decision.

---

## 1. Question

The maintained PETRA contract currently exposes LRPE directly as:

```text
LRPE : SHAPES -> N+
```

The tensor-materialization research established a faithful structural
representation:

```text
C : SHAPES -> STR
```

where one representative of `STR(S)` is:

```text
(root, M)
```

with:

- one local coordinate for every distinct rooted structural subform type;
- `root` selecting the root structural type;
- `M[i,j]` equal to the multiplicity of child type `j` under parent type `i`.

The factorization question is:

> Does there exist a PETRA interpretation function operating only on STR such
> that LRPE obtains exactly the same value?

Formally, does there exist:

```text
Λ_LRPE : STR -> N+
```

such that:

```text
LRPE
=
Λ_LRPE ∘ C
```

for every finite SHAPES form?

---

## 2. Existing LRPE semantics

For:

```text
S = Node(M_S)
```

let:

```text
supp(M_S)
```

be the set of distinct child structural classes.

The maintained LRPE interpretation assigns local ranks according to the
runtime's deterministic recursive structural order.

For child class `T`:

```text
rank_M(T)
=
1
+
|{ U in supp(M) : key(U) < key(T) }|.
```

The structural key is recursively:

```text
key(Z) = "()"
```

and:

```text
key(Node(children))
=
"("
+
concatenation of sorted child keys,
with multiplicity
+
")".
```

LRPE then uses:

```text
pair(m,v)
=
2^(m-1) * (2v-1)
```

and:

```text
LRPE(Z) = 1
```

while:

```text
LRPE(Node(M))
=
product over T in supp(M) of

p_rank_M(T)
^
pair(mult_M(T), LRPE(T)).
```

No occurrence path, object identity, sibling occurrence position, or
construction history participates in this definition.

---

## 3. STR dependency graph

For one STR representative:

```text
(root, M),
```

define a directed dependency:

```text
i -> j
```

exactly when:

```text
M[i,j] > 0.
```

Previous tensor-materialization results prove that this graph is:

```text
finite
acyclic
root-reachable
```

because every child structural type has strictly smaller height than its
parent structural type.

Therefore every coordinate can be evaluated bottom-up.

---

## 4. Structural key directly from STR

Define a key:

```text
K_M(i)
```

for every STR coordinate `i`.

If row `i` has no outgoing multiplicities:

```text
K_M(i) = "()".
```

Otherwise define:

```text
K_M(i)
=
"("
+
concatenation of
K_M(j) repeated M[i,j] times,
sorted lexicographically
+
")".
```

This recursion terminates because the STR dependency graph is finite and
acyclic.

No `Shape` object is reconstructed.

No occurrence-level data is needed.

The computation consumes only:

```text
M.
```

---

## 5. Structural-key reconstruction lemma

Let coordinate:

```text
pi(U)
```

represent SHAPES structural type `U`.

Then:

```text
K_M(pi(U))
=
key(U).
```

### Proof

Proceed by induction on:

```text
height(U).
```

### Base case

If:

```text
height(U) = 0,
```

then `U = Z`.

Its STR row contains no child multiplicities.

Therefore:

```text
K_M(pi(U))
=
"()"
=
key(Z).
```

### Inductive step

Assume the claim holds for every structural type of height less than `h`.

Let:

```text
height(U) = h > 0.
```

The row for `pi(U)` records exactly the multiplicity of each distinct child
structural type.

Every child type has smaller height.

By the induction hypothesis, each child coordinate reconstructs exactly the
runtime structural key of that child type.

Repeating each child key according to its matrix multiplicity and sorting
lexicographically therefore reconstructs exactly the canonical structural key
of `U`.

Hence:

```text
K_M(pi(U))
=
key(U).
```

Thus:

```text
STR_STRUCTURAL_KEY_RECONSTRUCTION=PROVED
```

---

## 6. Local LRPE ranks from STR

For one parent coordinate `i`, define its support:

```text
supp_M(i)
=
{ j | M[i,j] > 0 }.
```

Define the STR-derived local rank:

```text
rank_M_STR(i,j)
=
1
+
|{
    k in supp_M(i)
    :
    K_M(k) < K_M(j)
}|.
```

By structural-key reconstruction:

```text
K_M(pi(T))
=
key(T).
```

Therefore the ordering of child coordinates induced by `K_M` is exactly the
ordering LRPE applies to the corresponding child structural classes.

Hence:

```text
rank_M_STR(pi(U), pi(T))
=
rank_U(T).
```

for every child structural class `T` of `U`.

Thus:

```text
LRPE_LOCAL_RANK_RECOVERABLE_FROM_STR=PROVED
```

---

## 7. LAMBDA definition for LRPE

Define:

```text
V_M(i)
```

bottom-up on the STR dependency DAG.

For a zero-child row:

```text
V_M(i) = 1.
```

Otherwise:

```text
V_M(i)
=
product over j in supp_M(i) of

p_rank_M_STR(i,j)
^
pair(
    M[i,j],
    V_M(j)
).
```

Then define:

```text
Λ_LRPE(root, M)
=
V_M(root).
```

This function consumes only:

```text
root
M
```

and ordinary LRPE arithmetic.

It does not consume:

- a runtime `Shape`;
- `OccurrencePath`;
- object identity;
- sibling occurrence position;
- construction history;
- persistent structural-type identifiers.

---

## 8. LRPE factorization theorem

For every finite SHAPES structural type `U`:

```text
V_M(pi(U))
=
LRPE(U).
```

### Proof

Proceed by induction on:

```text
height(U).
```

### Base case

For:

```text
U = Z,
```

the corresponding STR row has no children.

Therefore:

```text
V_M(pi(Z))
=
1
=
LRPE(Z).
```

### Inductive step

Assume:

```text
V_M(pi(T))
=
LRPE(T)
```

for every structural child type `T` of `U`.

The STR row for `pi(U)` records exactly:

```text
mult_U(T)
```

for every distinct child structural type.

Section 6 proves that STR-derived local rank equals LRPE local structural rank:

```text
rank_M_STR(pi(U), pi(T))
=
rank_U(T).
```

By the induction hypothesis:

```text
V_M(pi(T))
=
LRPE(T).
```

Therefore every factor in the STR evaluation is exactly:

```text
p_rank_U(T)
^
pair(
    mult_U(T),
    LRPE(T)
),
```

which is precisely the corresponding factor in the maintained LRPE definition.

Hence:

```text
V_M(pi(U))
=
LRPE(U).
```

The result therefore holds for every structural type.

In particular, the root coordinate represents the complete input form `S`, so:

```text
Λ_LRPE(C(S))
=
LRPE(S).
```

Thus:

```text
LRPE
=
Λ_LRPE ∘ C.
```

Therefore:

```text
LRPE_STR_FACTORIZATION=PROVED
```

---

## 9. Coordinate-renaming invariance

STR coordinates have no intrinsic identity.

Let:

```text
sigma
```

be any permutation of the local coordinates.

Applying it simultaneously to the root selector and both matrix axes produces
another representative:

```text
(root', M')
```

of the same STR object.

Under this renaming:

```text
K_M'(sigma(i))
=
K_M(i)
```

because the recursive child multiplicities are unchanged modulo coordinate
names.

Therefore:

```text
rank_M'_STR(
    sigma(i),
    sigma(j)
)
=
rank_M_STR(i,j).
```

By induction over the dependency DAG:

```text
V_M'(sigma(i))
=
V_M(i).
```

In particular:

```text
Λ_LRPE(root', M')
=
Λ_LRPE(root, M).
```

Therefore `Λ_LRPE` is well-defined on the STR equivalence class modulo
simultaneous local-coordinate renaming.

Thus:

```text
LRPE_STR_COORDINATE_INVARIANCE=PROVED
```

---

## 10. Decoder independence

The existence proof for STR faithfulness previously established a decoder:

```text
Decode : STR -> SHAPES.
```

One could therefore define trivially:

```text
LRPE ∘ Decode.
```

That is not the result proved here.

The factorization established above evaluates LRPE directly from:

```text
root
+
child-type multiplicity matrix
```

using:

```text
structural-key reconstruction
+
local structural ranking
+
recursive LRPE arithmetic.
```

No runtime `Shape` reconstruction is required.

Therefore:

```text
SHAPE_DECODER_REQUIRED_BY_LAMBDA_LRPE=NO
```

This matters because it establishes STR as a sufficient mathematical input
boundary rather than merely as an alternate serialization from which the old
input object can be recovered first.

---

## 11. Probe 0 evidence

Before the proof, a bounded falsification probe evaluated the complete SHAPES
corpus through size 11:

```text
TOTAL_SHAPES=3047
```

The symbolic factorization test compared the complete LRPE recursive recipe
computed:

```text
directly from Shape
```

against the recipe computed:

```text
directly from STR.
```

Results:

```text
SYMBOLIC_FACTORIZATION_CASES=9139
COORDINATE_RENAMING_CASES=6092

FIRST_SYMBOLIC_FAILURE=NONE

SYMBOLIC_FACTORIZATION_GATE=PASS
COORDINATE_RENAMING_GATE=PASS
```

The larger count arises because each non-trivial local type vocabulary was
tested under multiple coordinate assignments.

A numeric runtime cross-check used explicit bounded materialization:

```text
NUMERIC_VALUE_CASES=398

RUNTIME_LIMIT_CASES=2649
STR_LIMIT_CASES=2649
LIMIT_AGREEMENT_CASES=2649

FIRST_NUMERIC_FAILURE=NONE

NUMERIC_RUNTIME_EQUIVALENCE_GATE=PASS
MATERIALIZATION_LIMIT_ALIGNMENT_GATE=PASS
```

The probe also established:

```text
STR_INPUT_ONLY=YES

SHAPE_DECODER_USED_BY_LAMBDA=NO
OCCURRENCE_PATH_USED=NO
OBJECT_IDENTITY_USED=NO
SIBLING_POSITION_SEMANTICS_USED=NO
LOCAL_COORDINATE_IDENTITY_USED=NO
```

The bounded probe is evidence.

The universal factorization claim rests on the proof above.

---

## 12. Architectural consequence

The maintained LRPE interpretation can now be expressed as:

```text
SHAPES
    |
    | C
    v
STR
    |
    | Λ_LRPE
    v
N+
```

with:

```text
LRPE
=
Λ_LRPE ∘ C.
```

Therefore PETRA's first maintained concrete interpretation does not require
access to structural information outside the faithful STR boundary.

The required information is exactly:

```text
root structural type
child structural-type dependencies
child multiplicities
recursive structural composition
```

No PETRA-specific semantic concept must be added to STR.

In particular STR does not need to contain:

```text
prime identity
exponent meaning
LRPE pairing semantics
PETRA numeric value
```

Those remain entirely inside:

```text
Λ_LRPE.
```

Thus the result supports the candidate boundary:

```text
SHAPES
    ↓
Tensor View
    ↓
STR
    ↓
LAMBDA
    ↓
interpretation semantics
```

with LRPE as the first concrete interpretation for which the factorization has
been proved.

---

## 13. What is not proved

This result does not prove that:

- every conceivable PETRA policy factors through the current STR;
- every future interpretation must consume STR;
- STR must become a mandatory architectural layer;
- `docs/VISION.md` should be changed automatically;
- `docs/reference/PETRA.md` should immediately replace direct SHAPES input;
- runtime PETRA must immediately be refactored to consume STR;
- COLLATZ factorization has been established.

Those are separate questions.

The theorem proves only:

```text
the maintained LRPE interpretation factors through faithful STR.
```

---

## 14. Factorization proof gate

```text
STR_STRUCTURAL_KEY_RECONSTRUCTION=PROVED

LRPE_LOCAL_RANK_RECOVERABLE_FROM_STR=PROVED

LAMBDA_LRPE_DEFINED_DIRECTLY_ON_STR=YES

LRPE_STR_FACTORIZATION=PROVED

LRPE_STR_COORDINATE_INVARIANCE=PROVED

SHAPE_DECODER_REQUIRED_BY_LAMBDA_LRPE=NO

PETRA_SPECIFIC_SEMANTICS_ADDED_TO_STR=NO

OCCURRENCE_IDENTITY_REQUIRED=NO
PERSISTENT_TYPE_ID_REQUIRED=NO
SIBLING_ORDER_REQUIRED=NO
CONSTRUCTION_HISTORY_REQUIRED=NO

NORMATIVE_CHANGE=NONE
RUNTIME_CHANGE=NONE

PETRA_STR_FACTORIZATION_PROOF_GATE=PASS
```

---

## 15. Research verdict

The PETRA / STR factorization question for maintained LRPE is closed:

```text
C : SHAPES -> STR

Λ_LRPE : STR -> N+

LRPE = Λ_LRPE ∘ C
```

for every finite SHAPES form.

The bounded Probe 0 produced no counterexample.

The general proof establishes the result independently of the bounded corpus.

This makes LRPE the first concrete maintained interpretation demonstrating
that the candidate STR/LAMBDA boundary is sufficient for real interpretation
semantics.

The next gate is no longer:

```text
CAN PETRA / LRPE FACTOR THROUGH STR?
```

The answer is:

```text
YES — PROVED.
```

The next architectural decision may therefore evaluate promotion of:

```text
SHAPES
    ↓
Tensor View
    ↓
STR
    ↓
LAMBDA
    ↓
interpretations
```

or separately investigate another interpretation such as COLLATZ before
promotion.

No such promotion is performed by this note.
