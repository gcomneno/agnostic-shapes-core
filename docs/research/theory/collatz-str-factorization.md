# COLLATZ / STR Factorization

## Status

Research result.

Non-normative.

This note studies a second interpretation over the promoted STR / LAMBDA
boundary.

It does not modify:

- SHAPES semantics;
- PETRA semantics;
- the STR architecture decision;
- runtime APIs;
- public behavior;
- `docs/VISION.md`;
- `docs/reference/SPEC.md`;
- `docs/reference/PETRA.md`.

The purpose is architectural falsification:

> Can an interpretation that is semantically independent from PETRA consume
> STR directly without requiring PETRA-specific information to leak into STR?

---

## 1. Research question

Let:

```text
C : SHAPES -> STR
```

be the promoted faithful Tensor View transduction.

Define a candidate structural seed function:

```text
χ : SHAPES -> N+
```

recursively by:

```text
χ(Z) = 1
```

and, for:

```text
U = Node(M_U),
```

define:

```text
χ(U)
=
1
+
Σ over T in supp(M_U)
    mult_U(T) * (χ(T) + 1)^2.
```

The question is whether there exists a direct STR interpretation:

```text
Λ_COLLATZ : STR -> N+
```

such that:

```text
χ
=
Λ_COLLATZ ∘ C
```

for every finite SHAPES form.

The interpretation must operate directly on STR.

It must not use:

```text
STR -> Shape -> χ
```

as its evaluation mechanism.

---

## 2. Why this is independent from PETRA

The candidate deliberately does not use:

- prime identities;
- prime assignment;
- LRPE local ranks;
- exponent semantics;
- exponent pairing;
- PETRA numeric values;
- integer factorization;
- sibling occurrence positions;
- occurrence paths;
- object identity;
- construction history.

Its only structural inputs are:

```text
root structural type
child structural-type dependencies
child multiplicities
recursive structure
```

These are already carried by STR.

The interpretation-specific arithmetic is only:

```text
addition
multiplication by multiplicity
squaring
```

and later:

```text
parity
ordinary Collatz dynamics
```

None of these concepts are added to STR.

---

## 3. Direct SHAPES seed

For the zero-child form:

```text
χ(Z) = 1.
```

For any non-zero-child structural type `U`:

```text
χ(U)
=
1
+
Σ over T in supp(U)
    mult_U(T) * (χ(T) + 1)^2.
```

Because sibling order is non-intrinsic, the definition ranges over distinct
child structural types and uses intrinsic multiplicity.

Equivalently, it could sum over child occurrences; grouping equal child types
produces exactly the displayed formula.

Therefore `χ` is a structural function.

It depends on neither sibling ordering nor occurrence identity.

---

## 4. STR representative

For one finite SHAPES form, let an STR representative be:

```text
(root, M)
```

where:

```text
M[i,j]
```

is the multiplicity of child structural type `j` under parent structural type
`i`.

The dependency relation:

```text
i -> j
```

holds when:

```text
M[i,j] > 0.
```

The promoted STR results establish that this dependency graph is finite and
acyclic.

Every child structural type has strictly smaller height than its parent type.

Therefore recursive bottom-up evaluation terminates.

---

## 5. Direct STR evaluation

Define:

```text
X_M(i)
```

for every STR coordinate `i` by:

```text
X_M(i)
=
1
+
Σ_j
    M[i,j] * (X_M(j) + 1)^2.
```

For a zero row:

```text
M[i,j] = 0
```

for every `j`, so automatically:

```text
X_M(i) = 1.
```

The definition consumes only:

```text
M.
```

No runtime `Shape` is reconstructed.

Now define:

```text
Λ_COLLATZ(root, M)
=
X_M(root).
```

Thus:

```text
Λ_COLLATZ : STR -> N+.
```

---

## 6. Seed reconstruction theorem

Let:

```text
pi(U)
```

be the local STR coordinate representing structural type `U`.

Then:

```text
X_M(pi(U))
=
χ(U).
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

then:

```text
U = Z.
```

The corresponding STR row has no child dependencies.

Therefore:

```text
X_M(pi(Z))
=
1
=
χ(Z).
```

### Inductive step

Assume:

```text
X_M(pi(T))
=
χ(T)
```

for every structural type of height less than `h`.

Let:

```text
height(U) = h > 0.
```

Every child structural type `T` of `U` has height less than `h`.

The STR row for `pi(U)` records exactly:

```text
M[pi(U), pi(T)]
=
mult_U(T).
```

By the induction hypothesis:

```text
X_M(pi(T))
=
χ(T).
```

Substituting into the STR recurrence:

```text
X_M(pi(U))
=
1
+
Σ_T
    M[pi(U), pi(T)]
    * (X_M(pi(T)) + 1)^2
```

gives:

```text
X_M(pi(U))
=
1
+
Σ_T
    mult_U(T)
    * (χ(T) + 1)^2.
```

But this is exactly:

```text
χ(U).
```

Therefore:

```text
X_M(pi(U))
=
χ(U).
```

for every finite structural type `U`.

Thus:

```text
COLLATZ_SEED_RECONSTRUCTION=PROVED
```

---

## 7. Factorization theorem

For any finite SHAPES form `S`, the root coordinate of:

```text
C(S)
```

represents `S` itself.

By the seed reconstruction theorem:

```text
Λ_COLLATZ(C(S))
=
χ(S).
```

Therefore:

```text
χ
=
Λ_COLLATZ ∘ C.
```

Hence:

```text
COLLATZ_STR_FACTORIZATION=PROVED
```

This factorization is direct.

It does not use:

```text
Decode : STR -> SHAPES
```

as an intermediate evaluation step.

Therefore:

```text
SHAPE_DECODER_REQUIRED_BY_LAMBDA_COLLATZ=NO
```

---

## 8. Coordinate-renaming invariance

STR coordinates have no intrinsic identity.

Let:

```text
sigma
```

be any permutation of the local coordinate set.

Simultaneously rename:

```text
root -> sigma(root)
```

and:

```text
M[i,j]
->
M'[sigma(i), sigma(j)].
```

We prove:

```text
X_M'(sigma(i))
=
X_M(i)
```

for every coordinate `i`.

Proceed bottom-up over the finite dependency DAG.

For a zero row, both sides are:

```text
1.
```

Assume the claim holds for every child coordinate `j` of `i`.

Then:

```text
X_M'(sigma(i))
=
1
+
Σ_j
    M'[sigma(i), sigma(j)]
    * (X_M'(sigma(j)) + 1)^2.
```

By simultaneous renaming:

```text
M'[sigma(i), sigma(j)]
=
M[i,j].
```

By the induction hypothesis:

```text
X_M'(sigma(j))
=
X_M(j).
```

Therefore:

```text
X_M'(sigma(i))
=
X_M(i).
```

In particular:

```text
Λ_COLLATZ(root', M')
=
Λ_COLLATZ(root, M).
```

Thus `Λ_COLLATZ` is well-defined on the STR object modulo local-coordinate
renaming.

Therefore:

```text
COLLATZ_STR_COORDINATE_INVARIANCE=PROVED
```

---

## 9. Ordinary Collatz dynamics

Define the ordinary Collatz step:

```text
κ : N+ -> N+
```

by:

```text
κ(n)
=
n / 2
```

when `n` is even, and:

```text
κ(n)
=
3n + 1
```

when `n` is odd.

The structural interpretation ends at:

```text
Λ_COLLATZ : STR -> N+.
```

Parity and Collatz dynamics begin only after this interpretation step.

Define the infinite deterministic Collatz trajectory map:

```text
K : N+ -> (N+)^N
```

by:

```text
K(n)_0 = n
```

and:

```text
K(n)_(t+1)
=
κ(K(n)_t).
```

No termination assumption is required.

No claim about the Collatz conjecture is made.

Define the full candidate semantic observation:

```text
J_COLLATZ : SHAPES -> (N+)^N
```

by:

```text
J_COLLATZ(S)
=
K(χ(S)).
```

Using the factorization theorem:

```text
χ
=
Λ_COLLATZ ∘ C,
```

therefore:

```text
J_COLLATZ
=
K ∘ Λ_COLLATZ ∘ C.
```

Thus the complete ordinary Collatz trajectory is determined above the same STR
boundary.

No parity or trajectory data must be stored in STR.

---

## 10. Interpretation is not required to be faithful

LAMBDA is an interpretation contract.

It is not a requirement that every:

```text
Λ_I
```

be injective.

The bounded Probe 0 found:

```text
TOTAL_SHAPES=3047
DISTINCT_SEEDS=2901
COLLISION_BUCKETS=138
```

and specifically:

```text
SIZE=10
FORMS=719
DISTINCT_COLLATZ_SEEDS=717

SIZE=11
FORMS=1842
DISTINCT_COLLATZ_SEEDS=1835
```

Therefore the candidate COLLATZ seed is not faithful on the tested corpus.

This is not a failure of the STR boundary.

STR itself remains faithful.

The information loss occurs intentionally inside:

```text
Λ_COLLATZ.
```

This demonstrates an important architectural distinction:

```text
faithful representation
    STR

interpretation-specific projection
    LAMBDA
```

A semantic consumer may deliberately collapse distinct structural forms.

---

## 11. Not merely structural size

Probe 0 also falsified the possibility that the candidate is merely:

```text
χ(S) = f(size(S))
```

for some size-only function.

At size three:

```text
A = ((()))
χ(A) = 37

B = (()())
χ(B) = 9
```

while:

```text
size(A)
=
size(B)
=
3.
```

Therefore:

```text
χ
```

depends on recursive structural organization, not merely occurrence count.

Thus:

```text
COLLATZ_NOT_SIZE_ONLY=PROVED_BY_WITNESS
```

---

## 12. Probe 0 evidence

The complete corpus of SHAPES forms through size 11 was evaluated:

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

Direct SHAPES seed evaluation and direct STR evaluation agreed for every form:

```text
DIRECT_STR_EQUIVALENCE_CASES=3047
FIRST_FACTORIZATION_FAILURE=NONE
COLLATZ_STR_FACTORIZATION_GATE=PASS
```

Coordinate-renaming tests produced:

```text
COORDINATE_RENAMING_CASES=6092
FIRST_COORDINATE_RENAMING_FAILURE=NONE
COLLATZ_STR_COORDINATE_INVARIANCE_GATE=PASS
```

Twenty-four-step Collatz trajectory prefixes agreed for every form:

```text
COLLATZ_PREFIX_CASES=3047
COLLATZ_PREFIX_STEPS=24
FIRST_TRAJECTORY_FAILURE=NONE
COLLATZ_TRAJECTORY_ALIGNMENT_GATE=PASS
```

The probe used no:

```text
Shape decoder
prime identity
LRPE local rank
exponent pairing
PETRA numeric value
sibling-position semantics
OccurrencePath
object identity
construction history
```

and inserted neither parity nor Collatz dynamics into STR.

The bounded probe is empirical evidence.

The universal factorization and coordinate-invariance claims rest on the proofs
above.

---

## 13. Architectural consequence

PETRA/LRPE was the first concrete consumer shown to factor through STR:

```text
SHAPES
    ↓ C
STR
    ↓ Λ_LRPE
N+
```

COLLATZ now supplies a second interpretation with deliberately different
semantics:

```text
SHAPES
    ↓ C
STR
    ↓ Λ_COLLATZ
N+
    ↓ K
Collatz trajectory
```

The two interpretation functions do not share interpretation-specific
machinery:

```text
Λ_LRPE
    prime assignment
    structural local ranking
    exponent pairing
    recursive prime/exponent arithmetic

Λ_COLLATZ
    multiplicity-weighted recursive polynomial seed
    followed by parity-driven Collatz dynamics
```

Their shared dependency is only structural:

```text
root
child-type dependencies
multiplicity
recursive structure
```

Those are STR concepts.

Therefore this second interpretation strengthens the evidence that STR is an
agnostic common representation boundary rather than a representation tailored
to PETRA.

No PETRA-specific concept must be introduced into STR to support COLLATZ.

No COLLATZ-specific concept must be introduced into STR either.

Thus:

```text
SECOND_INTERPRETER_BOUNDARY_VALIDATION=PROVED
```

for this concrete second interpretation.

---

## 14. What this does not prove

This result does not prove that:

- every conceivable interpretation factors through STR;
- STR must become mandatory for every interpretation;
- every useful interpretation should map into positive integers;
- `Λ_COLLATZ` is injective;
- the Collatz conjecture is true;
- every generated Collatz trajectory reaches `1`;
- COLLATZ should become a production runtime package;
- runtime STR APIs should now be implemented;
- PETRA runtime should now migrate to STR;
- Operational History belongs in LAMBDA;
- the existing architecture ADR should automatically be strengthened.

Those remain separate questions.

---

## 15. Proof gate

The established results are:

```text
COLLATZ_SEED_FUNCTION_WELL_DEFINED=PROVED

COLLATZ_SEED_IS_STRUCTURAL=PROVED

LAMBDA_COLLATZ_DEFINED_DIRECTLY_ON_STR=YES

COLLATZ_SEED_RECONSTRUCTION=PROVED

COLLATZ_STR_FACTORIZATION=PROVED

COLLATZ_STR_COORDINATE_INVARIANCE=PROVED

COLLATZ_TRAJECTORY_FACTORIZATION=PROVED

SHAPE_DECODER_REQUIRED_BY_LAMBDA_COLLATZ=NO

PRIME_IDENTITY_REQUIRED=NO

LRPE_LOCAL_RANK_REQUIRED=NO

EXPONENT_PAIRING_REQUIRED=NO

PETRA_NUMERIC_VALUE_REQUIRED=NO

SIBLING_ORDER_REQUIRED=NO

OCCURRENCE_IDENTITY_REQUIRED=NO

CONSTRUCTION_HISTORY_REQUIRED=NO

COLLATZ_PARITY_ADDED_TO_STR=NO

COLLATZ_DYNAMICS_ADDED_TO_STR=NO

COLLATZ_NOT_SIZE_ONLY=PROVED_BY_WITNESS

SECOND_INTERPRETER_BOUNDARY_VALIDATION=PROVED
```

Therefore:

```text
COLLATZ_STR_FACTORIZATION_PROOF_GATE=PASS
```

---

## 16. Research verdict

The second-interpreter validation succeeds.

For the candidate COLLATZ interpretation:

```text
χ
=
Λ_COLLATZ ∘ C
```

and:

```text
J_COLLATZ
=
K ∘ Λ_COLLATZ ∘ C.
```

The interpretation operates directly on STR, is invariant under local
coordinate renaming, does not reconstruct runtime SHAPES values, and does not
require PETRA-specific semantics.

The experiment therefore supports the promoted architecture:

```text
SHAPES
    ↓
Tensor View
    ↓
STR
   / \
  /   \
 ↓     ↓
Λ_LRPE Λ_COLLATZ
 ↓       ↓
PETRA    Collatz semantic domain
```

with two semantically independent concrete consumers.

Promotion beyond the existing ADR remains a separate explicit decision.

No runtime or normative change is made by this research result.
