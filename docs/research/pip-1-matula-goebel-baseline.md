# PIP-1 — Matula–Göbel baseline

Status: **Phase 3 research baseline — non-normative**

This note evaluates the classical Matula–Göbel numbering against the normative
PETRA interpretation contract in `docs/reference/PETRA.md`.

It does not introduce a PETRA runtime and does not promote the candidate to a
default PETRA policy.

## 1. Frozen research question

Can the classical Matula–Göbel numbering be expressed as a PETRA
prime/exponent interpretation over SHAPES, and if so, which PIP properties can
be established mathematically rather than inferred from bounded experiments?

The candidate must be evaluated against:

- structural admissibility;
- totality;
- prime validity;
- local prime injectivity;
- exponent semantics;
- computability;
- faithfulness;
- reachable image;
- reverse interpretation;
- materialization behavior.

## 2. Scope

The source domain is the complete SHAPES carrier:

```text
S ::= Node(M_f(S))
```

with:

```text
Z := Node(empty multiset).
```

The target is:

```text
N+ = {1, 2, 3, ...}.
```

No runtime API, serialization, CLI, schema, cache strategy, or implementation
limit is part of this research question.

## 3. Falsification criteria

The Matula–Göbel candidate fails as a conforming PETRA baseline if any of the
following is established:

1. its value depends on sibling order or occurrence identity;
2. equal SHAPES forms may receive different values;
3. some finite SHAPES form has no mathematical value;
4. distinct child-form classes can require the same prime base in one node;
5. the recursive definition is not well-founded;
6. the claimed injectivity fails;
7. the claimed correspondence with every positive integer fails;
8. reverse interpretation is not mathematically well-defined.

Implementation cost or large integer growth alone does not falsify the
mathematical interpretation; those belong to materialization analysis.

## 4. Possible outcome classes

The frozen outcomes are:

```text
A — incompatible with the PETRA contract
B — admissible but partial or non-faithful
C — admissible and faithful but not onto N+
D — admissible bijection S <-> N+
```

A result in class D still does not automatically make the policy normative or
the default PETRA runtime policy.

## 5. Prior work

David W. Matula introduced a natural enumeration of rooted trees by prime
factorization in 1968.

F. Göbel independently described and proved a one-to-one correspondence
between rooted trees and natural numbers in 1980.

Later literature refers to the resulting values as Matula numbers or
Matula–Göbel numbers.

Primary and direct references:

1. D. W. Matula, "A Natural Rooted Tree Enumeration by Prime Factorization",
   SIAM Review 10 (1968), p. 273.
2. F. Göbel, "On a 1-1-correspondence between rooted trees and natural
   numbers", Journal of Combinatorial Theory, Series B 29 (1980), 141–143.
   DOI: 10.1016/0095-8956(80)90049-0.
3. I. Gutman and A. Ivić, "On Matula numbers", Discrete Mathematics 150
   (1996), 131–142. DOI: 10.1016/0012-365X(95)00182-V.

Accordingly, PETRA makes no novelty claim for the Matula–Göbel bijection
itself.

## 6. Candidate definition

Let:

```text
p_n
```

denote the `n`-th prime:

```text
p_1 = 2
p_2 = 3
p_3 = 5
...
```

Define:

```text
MG(Z) = 1.
```

For:

```text
S = Node(M),
```

define:

```text
MG(S)
    =
∏[T ∈ supp(M)]
    p_{MG(T)} ^ mult_M(T).
```

Equivalently, without grouping equal children:

```text
MG(Node({T_1, ..., T_k}))
    =
∏[i=1..k] p_{MG(T_i)}.
```

The grouped form makes intrinsic SHAPES multiplicity explicit.

## 7. Expression in the PETRA `(A,E)` contract

The candidate can be written as:

```text
A_MG(M,T) = p_{MG(T)}
```

and:

```text
E_MG(m,v) = m.
```

Therefore:

```text
MG(Node(M))
    =
∏[T ∈ supp(M)]
    A_MG(M,T) ^ E_MG(mult_M(T), MG(T)).
```

The exponent policy ignores its recursive-value argument:

```text
E_MG(m,v) = m.
```

The recursive child value instead selects the prime base.

This is substantially different from the retired positional projection, where
prime identity was supplied by occurrence/address position.

## 8. Well-foundedness

`MG(T)` is needed only for proper child forms `T`.

Every proper child form has strictly smaller SHAPES size than its parent.

Therefore the definition is well-founded by induction on intrinsic SHAPES
size.

Base case:

```text
MG(Z) = 1.
```

Inductive step:

if `MG` is defined for every form of size less than `n`, then every child of a
size-`n` form already has a defined value, so the finite prime product is
defined.

Hence `MG` is total on every finite SHAPES form.

## 9. Structural admissibility

The candidate depends only on:

- each distinct child SHAPES form;
- its recursively determined Matula–Göbel value;
- its intrinsic multiplicity.

It does not depend on:

- sibling position;
- `OccurrencePath`;
- traversal order;
- object identity;
- construction history;
- historical PETRA ranks.

Permuting child occurrences therefore leaves the finite multiset unchanged and
does not alter the interpretation.

Equal child occurrences share the same prime base and contribute through the
base exponent equal to their multiplicity.

Therefore the candidate respects the SHAPES non-plane carrier.

## 10. Prime validity and local injectivity

Every base:

```text
p_{MG(T)}
```

is prime by definition.

Local injectivity follows once faithfulness of `MG` has been established:

```text
T != U
=>
MG(T) != MG(U)
=>
p_{MG(T)} != p_{MG(U)}.
```

Thus local prime injectivity and global faithfulness are naturally proved
together rather than treated as unrelated empirical properties.

## 11. Faithfulness

### Theorem

`MG` is injective on SHAPES forms.

### Proof

Proceed by induction on source size.

The unique size-one form is `Z`, with value `1`.

Assume injectivity has been established for every proper child form of two
forms:

```text
S = Node(M)
U = Node(N).
```

Suppose:

```text
MG(S) = MG(U).
```

By unique prime factorization, the two products have exactly the same prime
bases with exactly the same exponents.

A prime base appearing in either factorization has form:

```text
p_j
```

where:

```text
j = MG(T)
```

for one child-form class `T`.

Equality of prime bases therefore gives equality of the child Matula–Göbel
values.

By the inductive hypothesis, equal child values imply equal child SHAPES
forms.

Equality of prime exponents gives equality of the corresponding child
multiplicities.

Hence:

```text
M = N
```

as finite multisets of SHAPES forms, and therefore:

```text
S = U.
```

Thus `MG` is faithful. QED.

## 12. Reachable image

### Theorem

```text
Image(MG) = N+.
```

### Proof

Use induction on the target integer.

For:

```text
n = 1,
```

choose:

```text
Z.
```

Now let:

```text
n > 1.
```

Write its unique prime factorization as:

```text
n = ∏ p_j ^ e_j.
```

For every prime factor `p_j` of `n`:

```text
j < p_j <= n,
```

hence:

```text
j < n.
```

By induction there exists a SHAPES form `T_j` such that:

```text
MG(T_j) = j.
```

Construct the SHAPES form whose root child multiset contains exactly `e_j`
copies of each `T_j`.

Its Matula–Göbel value is:

```text
∏ p_{MG(T_j)} ^ e_j
=
∏ p_j ^ e_j
=
n.
```

Thus every positive integer is reachable. QED.

Combined with faithfulness:

```text
MG : SHAPES -> N+
```

is a bijection.

## 13. Reverse interpretation

The bijection gives a total reverse interpretation on `N+`.

Define:

```text
MG^-1(1) = Z.
```

For:

```text
n > 1,
```

factor:

```text
n = ∏ p_j ^ e_j.
```

Recursively decode each prime index:

```text
T_j = MG^-1(j).
```

Then construct:

```text
Node(
    multiset containing
    e_j copies of T_j
    for every prime factor p_j
).
```

The recursion terminates because every recursive index satisfies:

```text
j < n.
```

Unique prime factorization plus forward faithfulness makes the reverse result
single-valued up to SHAPES structural equality.

## 14. Computability

Forward interpretation is computable because:

1. every SHAPES form is finite;
2. recursion is by strictly decreasing subtree size;
3. the `n`-th prime is computable;
4. finite integer products and powers are computable.

Reverse interpretation is computable because:

1. integer prime factorization is computable;
2. prime indices are computable;
3. every recursive prime index is smaller than the current integer;
4. construction of the finite child multiset is effective.

This is a computability claim, not an efficiency claim.

Prime generation, factorization, and integer growth may be expensive.

## 15. Materialization

The mathematical interpretation is total, but concrete integer
materialization can grow rapidly.

Therefore a future runtime may impose:

- integer bit-length bounds;
- work budgets;
- prime-index bounds;
- recursion limits;
- factorization budgets.

Such refusal is:

```text
MATERIALIZATION_LIMIT_EXCEEDED
```

rather than semantic undefinedness.

The Matula–Göbel policy itself remains mathematically defined.

## 16. PIP classification

Against the Phase 3 PETRA contract:

```text
structurally admissible     YES
sibling-order invariant     YES
multiplicity preserving     YES
prime-valued                YES
locally prime-injective     YES
total on SHAPES             YES
computable                  YES
faithful                    YES
reachable image             N+
reverse interpretation      TOTAL ON N+
reverse single-valued       YES
requires SHAPES -> PETRA    NO
```

Frozen outcome:

```text
D — admissible bijection SHAPES <-> N+
```

## 17. Important consequence for PETRA

Matula–Göbel is not merely a convenient example.

It is a mathematically established control policy showing that the PETRA
contract admits at least one total, computable, faithful, reversible
prime/exponent interpretation whose reachable image is all positive integers.

Therefore future PIP candidates should be compared against this baseline.

Relevant questions include whether a candidate provides something not already
available from Matula–Göbel:

- different semantic information;
- a different reachable image;
- different computational behavior;
- different locality properties;
- different edit behavior;
- useful non-faithful quotient behavior;
- a meaningful interpretation equivalence class.

## 18. Novelty boundary

PETRA does not claim the following as new:

```text
rooted trees <-> positive integers
recursive prime-index encoding
Matula–Göbel numbering
prime-factor reverse decoding
```

Potential PETRA contribution must instead lie in the explicit architecture:

```text
SHAPES
    interpretation-agnostic structural carrier
        ↓
PETRA policy space
        ↓
PIP classification of prime/exponent interpretations
```

and in properties or policies beyond already-established rooted-tree
numberings.

## 19. Promotion boundary

This research result does not yet make Matula–Göbel:

- the default PETRA interpretation;
- a Python API;
- a package dependency;
- a CLI contract;
- a serialization;
- a schema;
- a runtime implementation.

Promotion requires a separate normative decision.

The next legitimate Phase 3 decision is whether Matula–Göbel should be:

1. retained only as the mandatory PIP control baseline;
2. admitted as one named PETRA policy;
3. selected as the initial reference PETRA policy.

Those are distinct decisions.
