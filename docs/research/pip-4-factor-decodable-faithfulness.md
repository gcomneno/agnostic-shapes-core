# PIP-4 — Factor-decodable sufficient conditions for faithfulness

Status: **Phase 3 research — general theorem — non-normative**

## 1. Purpose

PIP-1, PIP-2, and PIP-3 exhibit three materially different
prime/exponent interpretations over SHAPES:

```text
Matula–Göbel
    faithful

LRRE
    non-faithful

LRPE
    faithful
```

The purpose of PIP-4 is to extract a general sufficient condition explaining
both positive cases and the negative case.

The key observation is that unique prime factorization exposes, for every
distinct child-form class, one pair:

```text
(prime base, exponent).
```

Global faithfulness follows when that factor pair contains enough information
to recover:

```text
(child multiplicity, recursive child value).
```

This motivates the notion of a factor-decodable PETRA policy.

---

## 2. Frozen research question

For a PETRA interpretation:

```text
I(Z) = 1
```

and:

```text
I(Node(M))
    =
∏[T ∈ supp(M)]
    A(M,T) ^ E(mult_M(T), I(T)),
```

which local information-preservation condition is sufficient to imply:

```text
I(S) = I(U)
=>
S = U
```

for all SHAPES forms `S,U`?

---

## 3. Scope

This tranche studies sufficient conditions only.

It does not claim:

- necessity;
- classification of every faithful PETRA policy;
- minimality of the conditions;
- runtime API design;
- complexity bounds.

The result is mathematical research over the Phase 3 PETRA contract.

---

## 4. Local prime injectivity

Retain the normative PETRA requirement that, for every child multiset `M`:

```text
T != U
=>
A(M,T) != A(M,U)
```

for:

```text
T,U ∈ supp(M).
```

Thus each distinct child-form class contributes exactly one distinct prime
factor to the parent interpretation.

Unique prime factorization can therefore separate the contributions of
different child classes inside one interpreted node.

Local prime injectivity alone is not sufficient for global faithfulness.

PIP-2 already demonstrates this.

---

## 5. Factor code

For a child-form class:

```text
T ∈ supp(M),
```

with multiplicity:

```text
m = mult_M(T)
```

and recursive value:

```text
v = I(T),
```

define its **factor code** as:

```text
C_I(M,T)
    =
(
    A(M,T),
    E(m,v)
    ).
```

The parent value is exactly the product obtained from these factor codes:

```text
I(Node(M))
    =
∏ prime(C_I(M,T)) ^ exponent(C_I(M,T)).
```

Unique prime factorization recovers the finite mapping:

```text
prime -> exponent
```

from the resulting positive integer.

The question is therefore what semantic information can be recovered from
each such factor pair.

---

## 6. Factor decodability

### Definition

A PETRA interpretation policy is **factor-decodable** when there exists a
single partial decoder:

```text
D :
Primes × N+
⇀
N+ × N+
```

such that for every valid SHAPES node:

```text
Node(M)
```

and every:

```text
T ∈ supp(M),
```

if:

```text
m = mult_M(T)
v = I(T)
p = A(M,T)
e = E(m,v),
```

then:

```text
D(p,e) = (m,v).
```

The decoder need only be defined on factor pairs reachable under the policy.

It may use:

- the prime base;
- the exponent;
- both.

It must not require:

- sibling occurrence position;
- `OccurrencePath`;
- object identity;
- construction history;
- the original source form as hidden input.

Factor decodability means that no information needed to reconstruct the child
multiset is lost when one child class is encoded into its prime-power factor.

---

## 7. Why exponent injectivity alone is not the general condition

A tempting sufficient condition is:

```text
E(m,v)
```

injective in the pair `(m,v)`.

That condition is sufficient for policies such as LRPE, but it is stronger
than necessary.

Matula–Göbel uses:

```text
E_MG(m,v) = m.
```

This exponent function discards `v`.

Nevertheless Matula–Göbel is faithful because the prime base carries the
recursive value:

```text
A_MG(M,T) = p_v.
```

Hence:

```text
D_MG(p_v,m)
=
(m,v).
```

The correct general condition therefore concerns the joint factor:

```text
(prime, exponent),
```

not the exponent alone.

---

## 8. General faithfulness theorem

### Theorem

Let `I` be a PETRA interpretation on SHAPES satisfying:

1. `I(Z) = 1`;
2. every non-zero-child form has interpretation value greater than `1`;
3. prime assignment is locally injective on distinct child-form classes;
4. the policy is factor-decodable.

Then:

```text
I
```

is faithful on SHAPES.

### Proof

Proceed by strong induction on:

```text
size(S) + size(U).
```

#### Base case

The unique one-occurrence SHAPES form is:

```text
Z.
```

By assumption:

```text
I(Z) = 1.
```

Every non-zero-child form has value greater than `1`.

Therefore:

```text
I(S) = 1
```

implies:

```text
S = Z.
```

So equality involving the base form is uniquely determined.

#### Inductive step

Let:

```text
S = Node(M)
```

and:

```text
U = Node(N)
```

be non-zero-child forms and suppose:

```text
I(S) = I(U).
```

By unique prime factorization, the two integers have exactly the same finite
mapping:

```text
prime -> exponent.
```

Consider one factor:

```text
p^e.
```

in this common factorization.

Because the policy is factor-decodable:

```text
D(p,e) = (m,v)
```

uniquely recovers:

```text
m
```

and:

```text
v.
```

In `S`, local prime injectivity guarantees that the factor `p^e` belongs to
exactly one distinct child-form class `T` satisfying:

```text
mult_M(T) = m
```

and:

```text
I(T) = v.
```

In `U`, the same factor belongs to exactly one distinct child-form class `V`
satisfying:

```text
mult_N(V) = m
```

and:

```text
I(V) = v.
```

Both `T` and `V` are proper child forms.

Hence:

```text
size(T) + size(V)
<
size(S) + size(U).
```

By the inductive hypothesis:

```text
I(T) = I(V)
```

implies:

```text
T = V.
```

Therefore the common prime factor determines the same child SHAPES form and
the same intrinsic multiplicity in both parent forms.

Repeating this argument for every prime factor shows that `M` and `N` contain
exactly the same distinct child forms with exactly the same multiplicities.

Thus:

```text
M = N
```

as finite multisets, and therefore:

```text
S = U.
```

Hence `I` is faithful.

QED.

---

## 9. What the theorem actually requires

The theorem does not require prime bases themselves to globally identify
SHAPES forms.

Prime assignment may be:

- globally value-derived;
- locally ranked;
- context-sensitive;

provided that the complete reachable factor pair:

```text
(prime, exponent)
```

decodes unambiguously to:

```text
(multiplicity, recursive child value).
```

The recursive child value then identifies the child form inductively.

This separates two responsibilities:

```text
local factorization
    separates child classes

factor decoding
    preserves multiplicity + recursive value

induction
    recovers child structure
```

---

## 10. Matula–Göbel as a factor-decodable policy

Matula–Göbel uses:

```text
A_MG(M,T)
=
p_{MG(T)}
```

and:

```text
E_MG(m,v)
=
m.
```

A reachable factor:

```text
p_j ^ e
```

decodes as:

```text
D_MG(p_j,e)
=
(e,j).
```

Therefore:

```text
m = e
v = j.
```

Matula–Göbel is factor-decodable.

The general theorem therefore explains its faithfulness without requiring the
exponent itself to encode recursive child value.

---

## 11. LRPE as a factor-decodable policy

LRPE uses:

```text
A_LRPE(M,T)
=
p_{rank_M(T)}
```

and:

```text
E_LRPE(m,v)
=
pair(m,v),
```

with:

```text
pair(m,v)
=
2^(m-1) * (2v-1).
```

Because `pair` is bijective:

```text
unpair(E_LRPE(m,v))
=
(m,v).
```

Hence a decoder may simply use:

```text
D_LRPE(p,e)
=
unpair(e).
```

The prime component is not even required to recover `(m,v)`.

It remains necessary in the parent factorization to separate distinct local
child classes.

LRPE is therefore factor-decodable.

The general theorem explains the PIP-3 faithfulness result.

---

## 12. LRRE fails factor decodability

LRRE uses:

```text
E_LRRE(m,v)
=
m * v.
```

Its local prime assignment is structurally valid and locally injective.

However the factor:

```text
2^2
```

may arise from:

```text
(m,v) = (2,1)
```

or:

```text
(m,v) = (1,2).
```

Thus no decoder can satisfy simultaneously:

```text
D(2,2) = (2,1)
```

and:

```text
D(2,2) = (1,2).
```

LRRE is therefore not factor-decodable.

The general theorem correctly does not apply.

The concrete PIP-2 collision confirms the resulting loss of faithfulness.

---

## 13. Factor decodability versus local prime injectivity

These properties solve different problems.

### Local prime injectivity

Ensures that within one node:

```text
different child classes
```

do not collapse onto the same prime base.

### Factor decodability

Ensures that after arithmetic encoding, each prime-power factor retains enough
information to recover:

```text
multiplicity
+
recursive child interpretation.
```

Neither property should be silently substituted for the other.

PIP-2 demonstrates:

```text
local prime injectivity
without factor decodability
```

can still produce global collisions.

---

## 14. A useful stronger special case

A simple sufficient schema is:

```text
E : N+ × N+ -> N+
```

injective.

If `E` is injective on `(m,v)`, then an inverse on its reachable image gives:

```text
D(p,e)
=
E^-1(e).
```

Therefore any PETRA policy with:

1. locally injective prime assignment;
2. an injective exponent encoding of `(m,v)`;
3. `I(Z)=1`;
4. non-zero-child values greater than `1`;

is factor-decodable and hence faithful.

LRPE is an instance of this stronger schema.

Matula–Göbel is not, because its exponent ignores `v`; it satisfies the more
general joint-factor condition instead.

---

## 15. Another useful special case

A second sufficient schema places recursive identity in the prime base.

Suppose there exists an injective map:

```text
B : N+ -> Primes
```

such that:

```text
A(M,T)
=
B(I(T)),
```

and suppose the exponent uniquely determines multiplicity:

```text
E(m,v)
=
F(m)
```

for an injective:

```text
F : N+ -> N+.
```

Then:

```text
D(B(v), F(m))
=
(m,v).
```

Such a policy is factor-decodable.

Matula–Göbel is the canonical example with:

```text
B(v) = p_v
```

and:

```text
F(m) = m.
```

---

## 16. Information-placement duality

PIP-1 and PIP-3 reveal two distinct successful strategies.

### Recursive identity in the base

Matula–Göbel:

```text
base
    carries recursive value

exponent
    carries multiplicity
```

### Recursive identity in the exponent

LRPE:

```text
base
    carries local class separation

exponent
    carries multiplicity + recursive value
```

Thus PETRA faithfulness does not prescribe one unique semantic location for
recursive information.

What matters is recoverability of the combined factor data.

This is an important property of the PETRA interpretation-policy space.

---

## 17. Faithfulness is information preservation

The previous examples can now be summarized as:

```text
MG
factor pair preserves (m,v)
    ->
faithful

LRRE
factor pair loses (m,v)
    ->
collision

LRPE
factor pair preserves (m,v)
    ->
faithful
```

Therefore a central PIP question is not merely:

```text
which primes?
which exponents?
```

but:

```text
what information survives in each prime-power factor?
```

This gives a more useful research lens for constructing new PETRA policies.

---

## 18. Relationship to unique prime factorization

Unique prime factorization performs one role only:

```text
parent integer
    ->
unique finite map prime -> exponent.
```

It does not itself guarantee that a factor:

```text
p^e
```

uniquely determines the structural data from which it arose.

That additional property is precisely factor decodability.

Therefore:

```text
unique factorization
+
local prime injectivity
```

is not enough.

The sufficient mechanism established here is:

```text
unique factorization
+
local prime injectivity
+
factor decodability
+
structural induction
```

which yields:

```text
global faithfulness.
```

---

## 19. PIP classification theorem

The Phase 3 evidence now supports the implication:

```text
FACTOR-DECodable
+
LOCAL-PRIME-INJECTIVE
+
BASE-SEPARATED
=>
FAITHFUL
```

where `BASE-SEPARATED` means:

```text
I(Z) = 1
```

and every non-zero-child form has value greater than `1`.

More explicitly:

```text
local prime injectivity
        +
recoverable factor code
        +
well-founded structural recursion
        +
zero/non-zero value separation
        ↓
global faithfulness
```

This is a sufficient-condition theorem.

It is not claimed to be necessary.

---

## 20. Open questions

PIP-4 does not establish:

- whether every faithful PETRA interpretation admits some factor decoder;
- minimal sufficient conditions;
- necessary conditions for faithfulness;
- classification up to observational equivalence;
- conditions for surjectivity;
- conditions for decidable reachable image;
- complexity of forward or reverse interpretation;
- preservation or reflection of SHAPES ADD/REMOVE under arithmetic relations.

Those remain independent PIP questions.

---

## 21. Research outcome

PIP-4 generalizes the concrete Phase 3 policy results.

The principal result is:

> A locally prime-injective PETRA interpretation is faithful whenever every
> reachable prime/exponent factor unambiguously recovers the child
> multiplicity and recursively interpreted child value, provided the zero form
> is separated from every non-zero-child form.

This explains both successful Phase 3 reference/candidate policies:

```text
Matula–Göbel
LRPE
```

and exactly diagnoses the failure of:

```text
LRRE.
```

The important abstraction is therefore:

```text
factor-level information preservation.
```

That property is independent of whether recursive meaning is placed primarily
in prime bases, exponents, or both.
