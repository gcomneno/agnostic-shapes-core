# PIP-1 — Matula–Göbel reference interpretation

Status: **Phase 3 research — non-normative**

## 1. Purpose

This note evaluates the classical Matula–Göbel numbering as one mathematical
interpretation over the SHAPES carrier.

It is not treated as:

- the definition of PETRA;
- the preferred PETRA interpretation;
- the default PETRA policy;
- the origin of PETRA;
- the unique arithmetic interpretation of SHAPES.

Its role is narrower.

Matula–Göbel is a well-established external interpretation whose mathematical
structure happens to overlap strongly with the prime/exponent interpretation
space now reserved for PETRA.

It therefore provides a useful first reference object for the Prime
Interpretation Problem (PIP).

## 2. Architectural position

SHAPES is interpretation-agnostic.

Conceptually:

```text
                       SHAPES
                          |
        +-----------------+-----------------+
        |                 |                 |
 Matula–Göbel       Interpretation X      PETRA
                                            |
                                            +-- PIP
```

This diagram expresses conceptual roles, not compulsory implementation
dependencies.

Matula–Göbel may also be classified as a member of the PETRA policy space if
it satisfies the normative PETRA `(A,E)` interpretation contract.

That classification does not make Matula–Göbel synonymous with PETRA.

The general principle is:

```text
one SHAPES form
    ->
many possible mathematical interpretations
```

PETRA studies one particular family of those interpretations: recursive
prime/exponent interpretations.

## 3. Frozen research question

Can the classical Matula–Göbel numbering be expressed as an admissible PETRA
prime/exponent policy over SHAPES?

If so:

- is it total?
- is it structurally invariant?
- is it computable?
- is it faithful?
- what is its reachable image?
- does it admit a sound and complete reverse interpretation?

The purpose is classification, not promotion.

## 4. Falsification criteria

The candidate fails PETRA admissibility if any of the following holds:

1. its value depends on sibling ordering;
2. it depends on occurrence identity or runtime paths;
3. equal SHAPES forms can receive different values;
4. some finite SHAPES form has no mathematical value;
5. prime assignment violates the PETRA prime-assignment contract;
6. its recursive definition is not well-founded.

Claims of faithfulness, surjectivity, or reversibility fail independently if a
counterexample is found.

## 5. Possible outcomes

```text
A — not admissible under the PETRA contract
B — admissible but partial
C — admissible, total, but non-faithful
D — admissible, total and faithful, but not onto N+
E — admissible bijection SHAPES <-> N+
```

None of these outcomes automatically selects Matula–Göbel as a maintained
runtime policy.

## 6. Prior work

The correspondence predates PETRA.

Primary references include:

1. D. W. Matula, "A Natural Rooted Tree Enumeration by Prime Factorization",
   SIAM Review 10 (1968), p. 273.
2. F. Göbel, "On a 1-1-correspondence between rooted trees and natural
   numbers", Journal of Combinatorial Theory, Series B 29 (1980), 141–143.
   DOI: 10.1016/0095-8956(80)90049-0.
3. I. Gutman and A. Ivić, "On Matula numbers", Discrete Mathematics 150
   (1996), 131–142. DOI: 10.1016/0012-365X(95)00182-V.

PETRA therefore makes no novelty claim for the Matula–Göbel correspondence.

## 7. Candidate interpretation

Let:

```text
p_n
```

denote the `n`-th prime.

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

Equivalently, if child occurrences are written with repetition:

```text
MG(Node({T_1, ..., T_k}))
    =
∏[i=1..k] p_{MG(T_i)}.
```

The grouped form is preferable in the SHAPES setting because it exposes
intrinsic child multiplicity without introducing sibling order.

## 8. Expression as a PETRA policy

Under the normative PETRA contract:

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

The recursive child value selects the prime base.

Multiplicity supplies the exponent.

This is structurally different from the retired positional PETRA projection,
where prime identities were attached to representation positions.

## 9. Structural admissibility

The interpretation depends only on:

- a child SHAPES form;
- its recursively computed interpretation;
- its intrinsic multiplicity.

It does not depend on:

- sibling order;
- `OccurrencePath`;
- traversal order;
- object identity;
- allocation identity;
- construction history;
- historical positional ranks.

Equal child forms share the same prime base.

Their number of occurrences is represented by the corresponding prime
exponent.

Therefore sibling permutation cannot alter the resulting value.

The candidate is structurally admissible under the current PETRA contract.

## 10. Totality

Every proper child form has strictly smaller SHAPES size than its parent.

The recursion:

```text
MG(Z) = 1
```

followed by evaluation of child forms is therefore well-founded by induction
on SHAPES size.

Every finite support set yields a finite product of finite prime powers.

Hence `MG` is mathematically total on the SHAPES carrier.

## 11. Faithfulness

### Claim

`MG` is injective on SHAPES forms.

### Argument

Suppose:

```text
MG(Node(M)) = MG(Node(N)).
```

Unique prime factorization gives the same prime bases with the same exponents
on both sides.

A base:

```text
p_j
```

corresponds recursively to a child form whose Matula–Göbel value is `j`.

By induction on SHAPES size, equal recursive values identify equal child
SHAPES forms.

Equality of the corresponding prime exponents then identifies their intrinsic
multiplicities.

Therefore:

```text
M = N
```

as finite multisets, hence:

```text
Node(M) = Node(N).
```

Thus the interpretation is faithful.

## 12. Reachable image

Every positive integer has a unique factorization:

```text
n = ∏ p_j ^ e_j.
```

For `n = 1`, use `Z`.

For `n > 1`, every prime index `j` occurring in its factorization satisfies:

```text
j < n.
```

Recursively decode `j` to a SHAPES form `T_j`, then construct the root whose
child multiset contains `e_j` copies of each `T_j`.

The resulting form has value `n`.

Therefore:

```text
Image(MG) = N+.
```

Together with faithfulness:

```text
MG : SHAPES <-> N+
```

is a bijection.

## 13. Reverse interpretation

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

Recursively compute:

```text
T_j = MG^-1(j).
```

Then return:

```text
Node(
    multiset containing e_j copies of T_j
    for every factor p_j
).
```

Every recursive argument is smaller than the current integer, so the process
terminates.

Unique prime factorization and forward faithfulness make the result unique up
to SHAPES structural equality.

## 14. Computability versus efficiency

Both directions are computable.

Forward evaluation requires:

- recursive SHAPES traversal;
- computation of indexed primes;
- integer exponentiation and multiplication.

Reverse evaluation requires:

- integer factorization;
- recovery of prime indices;
- recursive decoding.

These statements establish computability, not practical efficiency.

Large values may make materialization prohibitively expensive.

That is a runtime-resource concern, not semantic undefinedness.

## 15. PIP classification

Current classification:

```text
structurally admissible     YES
sibling-order invariant     YES
multiplicity preserving     YES

prime-valued                YES
locally prime-injective     YES

total                       YES
computable                  YES
faithful                    YES

reachable image             N+
reverse interpretation      TOTAL ON N+
reverse single-valued       YES
```

Outcome:

```text
E — admissible bijection SHAPES <-> N+
```

## 16. Relationship to PETRA

This result does not mean:

```text
PETRA = Matula–Göbel
```

Instead:

```text
Matula–Göbel
    ∈
candidate PETRA prime/exponent interpretations
```

under the current `(A,E)` framework.

PETRA remains a policy space.

PIP studies which members of that space are:

- admissible;
- total;
- partial;
- faithful;
- non-faithful;
- computable;
- reversible;
- useful for particular mathematical purposes.

Matula–Göbel is therefore one reference interpretation among potentially many.

Its significance is that it demonstrates that the PETRA contract naturally
contains an already-established, mathematically strong interpretation.

That fact constrains novelty claims but does not collapse the PETRA research
programme into Matula–Göbel numbering.

## 17. What PETRA may still investigate

The existence of the Matula–Göbel bijection leaves substantial interpretation
space open.

Examples include policies with:

- different prime-assignment rules;
- different exponent semantics;
- deliberate non-faithful quotients;
- restricted reachable images;
- partial interpretation domains;
- different locality properties;
- different computational characteristics;
- different relationships with SHAPES edits;
- interpretation equivalence between distinct `(A,E)` formulations.

The PIP research object is therefore the policy space itself, not the recovery
of a single canonical numbering.

## 18. Promotion boundary

This document is research evidence.

It does not make Matula–Göbel:

- normative PETRA semantics;
- the default PETRA policy;
- the initial runtime implementation;
- a Python API;
- a CLI;
- a serialization;
- a schema.

Any such promotion requires a separate decision.

The result established here is only:

```text
Matula–Göbel is one mathematically established
prime/exponent interpretation compatible with
the current PETRA policy framework.
```
