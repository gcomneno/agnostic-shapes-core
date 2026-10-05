# PIP-2 — Local-Rank Recursive-Exponent interpretation

Status: **Phase 3 research — negative result — non-normative**

## 1. Purpose

This note studies a first PETRA-specific prime/exponent interpretation over
SHAPES.

The candidate deliberately retains one intuition from historical PETRA:

```text
recursive child meaning appears in an exponent
```

while removing the historical dependency on positional sibling ranks.

The purpose is not to preserve the old runtime.

The purpose is to ask whether a structurally legitimate version of that
prime/exponent idea is sufficient to produce a faithful interpretation.

It is not.

The smallest collision already occurs at SHAPES size three.

---

## 2. Frozen research question

Can a PETRA interpretation remain faithful when:

1. distinct child-form classes receive locally ranked prime bases; and
2. multiplicity and recursive child value are combined by ordinary
   multiplication in the exponent?

The candidate is called:

```text
LRRE
=
Local-Rank Recursive-Exponent
```

---

## 3. Scope

The source carrier is SHAPES:

```text
S ::= Node(M_f(S))
```

with:

```text
Z := Node(empty multiset).
```

The codomain is:

```text
N+.
```

This is research only.

No runtime, API, CLI, serialization, or schema is introduced.

---

## 4. Structural ordering used only for local prime assignment

LRRE needs a deterministic way to distinguish structurally different child
classes without using sibling position.

For this research candidate only, fix any computable total order:

```text
≺
```

on SHAPES forms satisfying:

```text
S = T
=>
neither S ≺ T nor T ≺ S
```

and depending only on SHAPES structure.

One concrete research construction is a recursively defined structural key:

```text
K(Z) = "()"
```

and for a non-zero-child form:

```text
K(Node(M))
    =
"("
+ lexicographically sorted concatenation of child K-values,
  with repetitions preserving intrinsic multiplicity
+ ")"
```

with a length-delimited implementation if executable representation is ever
required.

The key is introduced solely to induce a deterministic structural order for
this experiment.

It is not:

- SHAPES identity;
- a normative SHAPES serialization;
- an occurrence address;
- a persistent node identifier;
- a proposed public API.

---

## 5. Local structural rank

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

Thus distinct child-form classes are ranked:

```text
1, 2, ..., |supp(M)|
```

according only to their structural forms.

This is not sibling position.

Repeated occurrences of one structurally equal child form share one rank.

---

## 6. Prime-assignment policy

Let:

```text
p_n
```

be the `n`-th prime.

Define:

```text
A_LRRE(M,T)
    =
p_{rank_M(T)}.
```

Therefore the first structurally ranked child class receives prime `2`, the
second receives `3`, and so on.

Because ranking applies to distinct structural classes rather than child
occurrences:

- sibling permutation has no effect;
- equal child copies share one prime;
- local prime assignment is injective on `supp(M)`.

---

## 7. Exponent policy

Define:

```text
E_LRRE(m,v)
    =
m * v.
```

where:

```text
m
```

is intrinsic child multiplicity and:

```text
v
```

is the recursively interpreted child value.

The resulting interpretation is:

```text
LRRE(Z) = 1
```

and:

```text
LRRE(Node(M))
    =
∏[T ∈ supp(M)]
    p_{rank_M(T)} ^ (mult_M(T) * LRRE(T)).
```

This is a genuine recursive prime/exponent tower-style interpretation.

---

## 8. Frozen falsification criteria

The candidate fails the desired faithful-policy target if there exist distinct
SHAPES forms:

```text
S != T
```

such that:

```text
LRRE(S) = LRRE(T).
```

A single explicit collision is sufficient.

The candidate may still remain:

- structurally admissible;
- total;
- computable;
- locally prime-injective.

Those properties are classified independently.

---

## 9. Structural admissibility

LRRE uses only:

- SHAPES structural form;
- intrinsic child multiplicity;
- a structural total order over distinct child forms;
- recursively computed interpretation values.

It does not use:

- sibling occurrence position;
- `OccurrencePath`;
- runtime object identity;
- insertion history;
- memory identity;
- historical `Root(rank)` semantics.

Therefore it is invariant under sibling permutation and is admissible under the
current structural boundary of PETRA.

---

## 10. Totality

For every finite SHAPES form, recursive interpretation is evaluated only on
proper child forms.

Every child has strictly smaller SHAPES size.

The recursion therefore terminates by induction on size.

Local structural ranking is finite because every child multiset is finite.

Prime generation for a finite positive index and positive-integer
multiplication/exponentiation are mathematically defined.

Hence LRRE is total on SHAPES.

---

## 11. Computability

Given a computable structural ordering `≺`, LRRE is computable.

For each finite node:

1. compute the distinct child-form classes;
2. order them structurally;
3. assign the corresponding finite prime prefix;
4. recursively interpret each child form;
5. multiply multiplicity by recursive value;
6. form the finite prime-power product.

This establishes computability, not practical efficiency.

---

## 12. Minimal collision

Let:

```text
Z = Node(empty).
```

First define the one-child form:

```text
C = Node({Z}).
```

Since `Z` is its only distinct child class:

```text
rank_{ {Z} }(Z) = 1
```

and therefore:

```text
LRRE(C)
    =
2 ^ (1 * LRRE(Z))
    =
2 ^ 1
    =
2.
```

Now consider:

```text
S = Node({Z, Z})
```

and:

```text
T = Node({C}).
```

These SHAPES forms are structurally distinct.

`S` has root degree two.

`T` has root degree one.

For `S`, there is one distinct child-form class `Z` with multiplicity two:

```text
LRRE(S)
    =
2 ^ (2 * 1)
    =
4.
```

For `T`, there is one distinct child-form class `C` with multiplicity one and:

```text
LRRE(C) = 2.
```

Therefore:

```text
LRRE(T)
    =
2 ^ (1 * 2)
    =
4.
```

Hence:

```text
S != T
```

but:

```text
LRRE(S) = LRRE(T) = 4.
```

The interpretation is not faithful.

---

## 13. Cause of the collision

The failure is not caused by prime assignment.

Both examples contain only one distinct child class, so local prime assignment
correctly and unambiguously chooses:

```text
2.
```

The information loss occurs in:

```text
E_LRRE(m,v) = m * v.
```

The exponent cannot distinguish:

```text
(m,v) = (2,1)
```

from:

```text
(m,v) = (1,2).
```

Therefore the recursive interpretation conflates:

```text
two copies of a simpler child
```

with:

```text
one copy of a recursively more complex child.
```

This identifies the precise PIP defect.

---

## 14. General implication

Any exponent policy:

```text
E : N+ × N+ -> N+
```

used to encode both multiplicity and recursive child value risks this class of
collision whenever `E` is not injective on the relevant `(m,v)` pairs.

Thus:

```text
multiplicity-sensitive
```

is weaker than:

```text
pair-injective in (multiplicity, recursive value).
```

The PETRA specification deliberately did not assume such injectivity.

PIP-2 demonstrates why that distinction matters.

---

## 15. PIP classification

```text
structurally admissible     YES
sibling-order invariant     YES
multiplicity explicit       YES

prime-valued                YES
locally prime-injective     YES

total                       YES
computable                  YES

faithful                    NO
collision-free              NO

reachable image             NOT CLASSIFIED
reverse interpretation      NOT SINGLE-VALUED
```

The negative result is sufficient to reject LRRE as a faithful PETRA
interpretation.

---

## 16. Relationship to historical PETRA

LRRE is not a restoration of historical PETRA behavior.

It deliberately removes the historical positional-prime dependency.

However, it retains the historically interesting idea that recursive
interpretation values can live in exponents.

PIP-2 therefore isolates that idea cleanly and shows:

```text
recursive value in exponent
+
multiplicity by ordinary multiplication
```

is insufficient for faithfulness.

---

## 17. Consequence for the next candidate

The failure points directly to the next research question.

Instead of:

```text
E(m,v) = m * v,
```

use an injective encoding:

```text
E(m,v) = pair(m,v)
```

where:

```text
pair : N+ × N+ -> N+
```

is injective.

A particularly simple candidate is the two-adic pairing:

```text
pair(m,v)
    =
2^(m-1) * (2v-1).
```

Every positive integer has a unique decomposition into:

```text
power of 2
*
odd positive integer,
```

so this pairing is bijective:

```text
N+ × N+ <-> N+.
```

Whether replacing multiplication with this pairing is sufficient for a
faithful PETRA interpretation is the subject of the next PIP tranche.

---

## 18. Research outcome

Frozen outcome:

```text
LRRE
=
admissible
+
total
+
computable
+
non-faithful.
```

The failure is constructive and occurs at size three.

This is a useful PIP result.

It shows that PETRA cannot infer global faithfulness merely from:

- structurally invariant prime assignment;
- local prime injectivity;
- recursion;
- explicit multiplicity;
- unique prime factorization.

Information preservation inside the exponent policy matters independently.
