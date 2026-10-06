# PETRA Interpretation Specification

## Status and authority

This document is the normative specification for the PETRA interpretation
layer.

PETRA means:

```text
Prime Exponent Tower Recursive Algebra
```

PETRA is an interpretation layer over SHAPES.

The normative SHAPES carrier and intrinsic structural semantics remain defined
exclusively by:

```text
docs/reference/SPEC.md
```

This specification may constrain PETRA interpretation behavior, but it must
never redefine SHAPES structure.

The dependency direction is:

```text
PETRA -> SHAPES

SHAPES -X-> PETRA
```

PIP — the Prime Interpretation Problem — is foundational theory inside PETRA.
It is not a sibling core and is not an intermediate runtime layer between
PETRA and SHAPES.

Historical PET and pre-separation PETRA runtimes, representations, operators,
serializations, schemas, and arithmetic experiments are evidence only unless
explicitly admitted by this specification.

---

## Operational contract

The PETRA/SHAPES relationship can be summarized as:

```text
SHAPES form
    |
    | selected PETRA interpretation policy
    v
positive integer
```

SHAPES owns the form and its intrinsic structural operations.

PETRA consumes an already-existing SHAPES form and interprets it
arithmetically.

In particular:

```text
SHAPES
=
structure + structural equality + intrinsic edits

PETRA
=
arithmetic interpretation of that structure
```

For a selected PETRA policy `P`, the forward direction is:

```text
I_P : S ⇀ N+
```

where `S` is the SHAPES carrier.

This mapping may be partial.

PETRA does not use the resulting integer to define:

- SHAPES identity;
- SHAPES equality;
- SHAPES edit legality;
- SHAPES canonicalization.

A policy may additionally provide a reverse interpretation:

```text
R_P : N+ ⇀ S
```

but reverse interpretation is policy-specific and need not exist for every
PETRA policy or every positive integer.

When a policy is faithful and has an effective inverse on its reachable image,
the operational round trip is:

```text
SHAPES form
    |
    | I_P
    v
reachable integer
    |
    | R_P
    v
same SHAPES form
```

Thus PETRA is not an alternative structural core.

It is an arithmetic interpretation layer over SHAPES.

For the first maintained policy, LRPE, faithfulness and effective reverse
interpretation on `Image(LRPE)` are established separately in Section 18.

This section is a compact restatement of the contracts defined below. It does
not introduce additional PETRA semantics.

---

## 1. Source domain

Let `S` denote the canonical SHAPES carrier.

A SHAPES form has recursive presentation:

```text
S ::= Node(M_f(S))
```

where `M_f(S)` is a finite multiset of SHAPES forms.

Let:

```text
Z := Node(empty multiset)
```

PETRA consumes already-existing SHAPES forms.

PETRA does not construct the SHAPES carrier from integers, primes,
factorizations, exponent towers, or any other external values.

For every interpretation policy `P`, its semantic domain is some subset:

```text
D_P ⊆ S
```

An interpretation policy may be total:

```text
D_P = S
```

or partial.

Partiality must be explicit.

---

## 2. Interpretation codomain

The primary arithmetic codomain of PETRA is the set of positive integers:

```text
N+ = {1, 2, 3, ...}
```

For an interpretation policy `P`, PETRA defines a partial interpretation:

```text
I_P : S ⇀ N+
```

The value of a SHAPES form is interpretation output.

It is not:

- SHAPES identity;
- SHAPES equality;
- SHAPES size;
- occurrence identity;
- edit legality;
- structural canonicalization.

Two distinct SHAPES forms may receive the same PETRA value unless the selected
interpretation policy has separately been proved faithful.

---

## 3. Child-form support and multiplicity

For a finite child multiset `M`, define:

```text
supp(M)
```

as the finite set of distinct SHAPES forms occurring in `M`.

For:

```text
T ∈ supp(M)
```

let:

```text
mult_M(T) ∈ N+
```

be the intrinsic multiplicity of `T` in `M`.

PETRA operates on this multiset structure.

PETRA must not derive semantics from:

- sibling position;
- traversal order;
- `OccurrencePath`;
- insertion history;
- object identity;
- arbitrary ordering of equal child occurrences.

Structurally equal child copies therefore belong to the same support class.

Their multiplicity remains explicit.

---

## 4. Prime-assignment policy

A PETRA prime-assignment policy `A` assigns a prime to each distinct child form
in the support of one SHAPES node:

```text
A(M, T) -> prime
```

for:

```text
T ∈ supp(M)
```

whenever the policy is defined.

### 4.1 Prime validity

Every assigned value must be prime:

```text
A(M,T) ∈ Primes
```

### 4.2 Local injectivity

Within one child multiset, structurally distinct child forms must receive
distinct primes:

```text
T != U
=>
A(M,T) != A(M,U)
```

for:

```text
T,U ∈ supp(M)
```

This is local injectivity of prime bases.

It does not by itself imply injectivity of the complete PETRA interpretation.

### 4.3 Structural invariance

Prime assignment must depend only on SHAPES structure and the finite child
multiset being interpreted.

It must be invariant under sibling permutation.

It must not depend on:

- occurrence position;
- `OccurrencePath`;
- runtime object identity;
- memory address;
- construction history;
- a historical PETRA positional rank.

If two concrete realizations represent the same SHAPES form, prime assignment
must produce the same interpretation behavior.

### 4.4 Equal child copies

Multiple occurrences of the same child form do not receive arbitrary distinct
prime identities.

They share the prime associated with their structural child-form class.

Their multiplicity is handled by the exponent policy.

This prevents PETRA from introducing persistent identities merely to
distinguish symmetric copies.

---

## 5. Exponent policy

A PETRA exponent policy `E` maps:

```text
(m, v)
```

to a positive integer exponent, where:

```text
m ∈ N+
v ∈ N+
```

and:

- `m` is the intrinsic multiplicity of one child-form class;
- `v` is the recursively interpreted PETRA value of that child form.

Thus:

```text
E : N+ × N+ ⇀ N+
```

may be total or partial.

The exponent policy must be deterministic on its declared domain.

No particular historical exponent rule is admitted automatically.

In particular, rules such as:

```text
E(m,v) = m * v
```

are candidate policies, not axioms of PETRA.

Properties such as:

- injectivity in `m`;
- injectivity in `v`;
- injectivity on `(m,v)`;
- monotonicity;
- boundedness;

are independent policy properties to be studied by PIP.

---

## 6. Recursive PETRA interpretation

Given a prime-assignment policy `A` and exponent policy `E`, define the
associated interpretation recursively.

For the zero-child SHAPES form:

```text
I(Z) = 1
```

For:

```text
S = Node(M)
```

define:

```text
I(S)
    =
product over T in supp(M) of

A(M,T) ^ E(mult_M(T), I(T))
```

whenever every recursive interpretation, prime assignment, exponent
evaluation, and arithmetic result required by the expression is defined.

Equivalently:

```text
I(Node(M))
    =
∏[T ∈ supp(M)]
    A(M,T) ^ E(mult_M(T), I(T))
```

The empty product is `1`.

This recursion is downstream of SHAPES structure.

PETRA values never participate in SHAPES structural equality.

---

## 7. Interpretation partiality

Interpretation failure must be explicit.

At the semantic level, an interpretation may be undefined because:

- the prime-assignment policy is undefined for the current multiset;
- the exponent policy is undefined for a required `(m,v)` pair;
- a recursive child interpretation is undefined.

These are interpretation-domain failures.

They are distinct from implementation resource failures.

A runtime must not silently replace an undefined interpretation with:

- `0`;
- `1`;
- a fallback prime;
- a truncated value;
- a hash;
- an approximate result.

---

## 8. Materialization limits

Mathematical interpretation and runtime materialization are distinct.

An interpretation may be mathematically defined while a concrete runtime
refuses to materialize the resulting integer because of resource limits.

Possible runtime limits include:

- maximum exponent;
- maximum integer bit length;
- maximum recursion depth;
- maximum work budget;
- maximum prime-generation budget.

Such limits are engineering policy.

They are not PETRA mathematical semantics.

A runtime must distinguish at least conceptually between:

```text
INTERPRETATION_UNDEFINED
```

and:

```text
MATERIALIZATION_LIMIT_EXCEEDED
```

Increasing a runtime resource bound must not alter the mathematical value of an
already-defined interpretation.

---

## 9. Interpretation equivalence

Two PETRA interpretation policies:

```text
P
Q
```

are observationally equivalent when they have the same semantic domain and
produce the same value on every form in that domain:

```text
D_P = D_Q
```

and:

```text
for every S in D_P:

I_P(S) = I_Q(S)
```

This is the canonical interpretation-equivalence relation admitted by this
specification.

Internal implementation strategy, prime-generation algorithm, caching,
memoization, traversal strategy, or data representation do not distinguish
observationally equivalent policies.

Weaker equivalence notions may be studied by PIP but are not normative unless
explicitly promoted.

---

## 10. Faithfulness and injectivity

A PETRA interpretation `I` is faithful on its domain when:

```text
I(S) = I(T)
=>
S = T
```

for every:

```text
S,T ∈ D_I
```

Faithfulness is not assumed by the base PETRA interpretation contract.

It is a property that must be proved for a particular interpretation policy.

Neither:

- local distinctness of assigned primes;
- recursive evaluation;
- unique prime factorization;

alone proves global faithfulness.

In particular, multiplicity/exponent interactions and policy-dependent prime
assignment may create collisions.

PIP is responsible for identifying sufficient or necessary conditions for
faithfulness.

---

## 11. Reachable image

For an interpretation `I`, define its reachable image:

```text
Image(I)
    =
{ n ∈ N+ | exists S ∈ D_I such that I(S) = n }
```

PETRA does not assume:

```text
Image(I) = N+
```

Surjectivity onto all positive integers is therefore not part of the base
contract.

Questions such as:

- which integers are reachable;
- whether the image is decidable;
- whether image membership is computable;
- whether the image has arithmetic structure;

belong to policy-specific PETRA theory and PIP.

---

## 12. Reverse interpretation

A reverse interpretation is a partial map:

```text
R_I : N+ ⇀ S
```

associated with a particular forward interpretation `I`.

A reverse interpretation is sound when:

```text
R_I(n) = S
=>
I(S) = n
```

It is complete on the reachable image when:

```text
I(S) = n
=>
R_I(n) = S
```

for every `S` in the forward domain.

A single-valued complete reverse interpretation requires forward faithfulness.

Computability of a reverse interpretation is a separate property.

A mathematically existing inverse on the image is not automatically an
effective algorithm.

Factorization may be used by a PETRA reverse interpreter when justified by its
policy.

It must never become a prerequisite for SHAPES construction or conformance.

---

## 13. Computability

A PETRA policy may be classified as effectively computable when:

1. prime assignment is computable on every input in its declared domain;
2. exponent evaluation is computable on every required `(m,v)` pair;
3. recursive interpretation terminates for every form in the declared domain.

Because every SHAPES form is finite, structural recursion itself is
well-founded.

Non-computability or partiality may nevertheless arise from the selected
interpretation policies.

Runtime implementation requires an effectively computable policy.

Pure mathematical research may study broader policy classes.

---

## 14. PIP — Prime Interpretation Problem

The Prime Interpretation Problem is the foundational policy-classification
problem inside PETRA.

Given candidate policies:

```text
A = prime-assignment policy
E = exponent policy
```

PIP asks which properties the resulting interpretation possesses.

At minimum, a PIP analysis must consider:

### 14.1 Structural admissibility

Does the policy:

- respect SHAPES structural equality;
- ignore sibling permutation;
- preserve intrinsic multiplicity as explicit input;
- avoid persistent occurrence identity;
- avoid dependency on runtime paths or object identity?

### 14.2 Prime assignment

Is prime assignment:

- prime-valued;
- locally injective on distinct child forms;
- deterministic;
- total or explicitly partial;
- computable?

### 14.3 Exponent semantics

Is the exponent policy:

- positive-integer valued;
- deterministic;
- total or explicitly partial;
- multiplicity-sensitive;
- injective in either argument or jointly;
- computable?

### 14.4 Global interpretation

Is the resulting interpretation:

- well-defined;
- total or partial;
- computable;
- faithful;
- collision-free on a stated domain;
- observationally equivalent to another policy?

### 14.5 Reachable image

Can the image be:

- characterized;
- enumerated;
- decided;
- recognized efficiently?

### 14.6 Reverse interpretation

Does a reverse map:

- exist mathematically;
- remain single-valued;
- terminate effectively;
- require factorization;
- reconstruct SHAPES forms uniquely?

### 14.7 Resource behavior

Can values be materialized under explicit runtime bounds?

Resource failure must remain distinct from semantic undefinedness.

---

## 15. PIP evidence discipline

A candidate interpretation does not become normative because:

- it reproduces historical PET/PETRA values;
- it works on bounded examples;
- its values appear collision-free in a finite scan;
- prime factorization happens to decode tested examples.

For universal claims such as faithfulness, injectivity, or complete reverse
interpretability, bounded experiments are evidence only.

Promotion requires an appropriate proof or a deliberately bounded normative
claim.

Negative results and counterexamples are first-class PIP results.

---

## 16. Required separation from SHAPES

PETRA must never redefine:

- the SHAPES carrier;
- structural equality;
- child multiplicity;
- sibling non-order;
- occurrence semantics;
- `OccurrencePath`;
- intrinsic `ADD`;
- intrinsic `REMOVE`;
- intrinsic SHAPES size.

In particular:

```text
I(S) = I(T)
```

does not imply:

```text
S = T
```

unless faithfulness of `I` has separately been established.

Likewise, PETRA values cannot make an otherwise illegal SHAPES edit legal or an
otherwise legal SHAPES edit illegal.

---

## 17. Runtime admission boundary

This specification defines interpretation semantics.

It does not yet define a Python API.

The following remain separate implementation decisions:

- Python package layout;
- concrete policy interfaces;
- default interpretation policy;
- prime generator;
- integer materialization strategy;
- caching;
- serialization;
- CLI;
- schema namespace;
- error classes;
- reverse-decoding API.

No historical pre-separation PETRA runtime interface is restored by default.

Implementation begins only after this contract is accepted.

---

## 18. First maintained interpretation policy

Phase 3 PIP research establishes the first maintained PETRA interpretation
policy:

```text
LRPE
=
Local-Rank Paired-Exponent
```

This promotion is intentionally narrow.

It does not mean:

```text
PETRA = LRPE
```

and it does not make LRPE the only valid PETRA interpretation.

PETRA remains a prime/exponent interpretation-policy space over SHAPES.

LRPE is the first concrete policy selected for maintained runtime
implementation because the Phase 3 research establishes that it is:

- structurally admissible;
- sibling-order invariant;
- total on SHAPES;
- effectively computable;
- locally prime-injective;
- factor-decodable;
- faithful;
- non-surjective onto `N+`;
- equipped with a decidable reachable image;
- equipped with an effective single-valued inverse on that image.

### 18.1 LRPE structural ranking

For every finite child multiset `M`, distinct child-form classes are ordered by
a deterministic total order depending only on SHAPES structure.

For:

```text
T ∈ supp(M),
```

define:

```text
rank_M(T)
=
1 + |{ U ∈ supp(M) : U ≺ T }|.
```

The order used by the runtime must be:

- deterministic;
- structural;
- independent of sibling occurrence position;
- independent of `OccurrencePath`;
- independent of object identity and construction history.

The runtime representation used to compute this order is an implementation
detail and does not become SHAPES identity or serialization.

### 18.2 LRPE prime assignment

Let `p_n` denote the `n`-th prime.

LRPE assigns:

```text
A_LRPE(M,T)
=
p_{rank_M(T)}.
```

Thus distinct child classes receive distinct local prime bases.

Equal child copies share one prime base.

### 18.3 LRPE exponent policy

Define:

```text
pair(m,v)
=
2^(m-1) * (2v-1).
```

Then:

```text
E_LRPE(m,v)
=
pair(m,v).
```

The pairing is bijective on:

```text
N+ × N+
```

with inverse obtained from the two-adic decomposition:

```text
e = 2^a * q
```

where `q` is odd:

```text
m = a + 1
v = (q + 1) / 2.
```

### 18.4 LRPE forward interpretation

LRPE therefore interprets:

```text
LRPE(Z) = 1
```

and:

```text
LRPE(Node(M))
    =
∏[T ∈ supp(M)]
    p_{rank_M(T)}
    ^
    pair(mult_M(T), LRPE(T)).
```

### 18.5 LRPE image

LRPE is faithful but not surjective onto `N+`.

Every non-unit reachable value has prime support equal to an initial prime
segment:

```text
{p_1, ..., p_k}
```

and every exponent must decode recursively to a valid child multiplicity and
reachable child value whose structural order agrees with the corresponding
local rank.

The reachable image is decidable by the maintained reverse interpreter.

### 18.6 LRPE reverse interpretation

The maintained LRPE reverse interpreter is partial over `N+` and total on:

```text
Image(LRPE).
```

It must:

1. map `1` to `Z`;
2. factor non-unit inputs;
3. reject non-contiguous prime support;
4. unpair every exponent;
5. recursively decode child values;
6. reject duplicate decoded child classes;
7. verify structural-rank consistency;
8. reconstruct intrinsic multiplicity;
9. return the resulting SHAPES form.

Every recursive child value is strictly smaller than the current integer, so
the algorithm terminates.

Failure because an integer is outside the LRPE image is semantic reverse-domain
failure, not a materialization-limit failure.

### 18.7 Matula–Göbel status

Matula–Göbel remains a mathematically established reference interpretation and
a valid PIP comparison object.

It is not selected as the initial maintained PETRA runtime policy.

PETRA makes no novelty claim for Matula–Göbel numbering or its
integer/rooted-tree bijection.

### 18.8 Explicit policy selection

The initial runtime must not silently define:

```text
PETRA value = LRPE value.
```

The architecture must preserve policy identity explicitly.

LRPE may be the only maintained executable policy initially, but public
interpretation operations must still make the selected policy concept
explicit rather than collapsing PETRA into one arithmetic mapping.

No implicit universal default policy is established by this specification.

---

## 19. Initial Phase 3 conformance checklist

The initial PETRA runtime must:

- depend on SHAPES;
- accept SHAPES forms as interpretation input;
- keep SHAPES independent of PETRA;
- implement only explicitly selected prime/exponent policies;
- provide LRPE as the first maintained interpretation policy;
- preserve explicit policy identity even while LRPE is the only maintained
  executable policy;
- preserve sibling permutation invariance;
- represent multiplicity explicitly in exponent semantics;
- distinguish semantic partiality from materialization limits;
- make faithfulness an established property, not an assumption;
- define reachable-image claims precisely;
- define reverse interpretation only when its contract is justified;
- expose no compatibility behavior merely because historical PETRA exposed it.

PIP remains the mechanism for deciding which concrete interpretation policy is
worthy of becoming the first maintained PETRA runtime policy.
