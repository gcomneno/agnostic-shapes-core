# PIP-3 — Local-Rank Paired-Exponent interpretation

Status: **Phase 3 research — positive faithfulness result — non-normative**

## 1. Purpose

PIP-2 established that the Local-Rank Recursive-Exponent interpretation:

```text
E(m,v) = m * v
```

is not faithful.

The minimal collision was:

```text
(m,v) = (2,1)
```

versus:

```text
(m,v) = (1,2).
```

Both produce exponent `2`.

PIP-3 changes exactly one component.

The local structural prime-assignment policy is retained.

The exponent policy is replaced by an injective pairing of:

```text
multiplicity
+
recursive child value.
```

The resulting candidate is called:

```text
LRPE
=
Local-Rank Paired-Exponent.
```

---

## 2. Frozen research question

Is pair-injective exponent encoding sufficient to make the local-rank
prime-assignment interpretation faithful on SHAPES?

The properties to classify are:

- structural admissibility;
- totality;
- computability;
- prime validity;
- local prime injectivity;
- exponent pair-injectivity;
- global faithfulness;
- reachable image;
- reverse interpretation.

---

## 3. Scope

The source carrier remains:

```text
S ::= Node(M_f(S))
```

with:

```text
Z := Node(empty multiset).
```

The codomain remains:

```text
N+.
```

No runtime implementation is introduced.

---

## 4. Structural child ordering

Retain the same research-level structural total order:

```text
≺
```

used by PIP-2.

For:

```text
T ∈ supp(M),
```

define:

```text
rank_M(T)
=
1 + |{U ∈ supp(M) : U ≺ T}|.
```

Ranks therefore form exactly:

```text
1, 2, ..., |supp(M)|.
```

This order is defined only from SHAPES structure.

It is not:

- sibling occurrence position;
- `OccurrencePath`;
- persistent identity;
- historical PETRA rank ontology.

---

## 5. Prime-assignment policy

Let:

```text
p_n
```

be the `n`-th prime.

Define:

```text
A_LRPE(M,T)
=
p_{rank_M(T)}.
```

Hence distinct structural child classes receive distinct primes locally.

Repeated occurrences of one child form share the same prime base.

---

## 6. Exponent pairing

Define:

```text
pair(m,v)
=
2^(m-1) * (2v-1)
```

for:

```text
m,v ∈ N+.
```

### Theorem — pair is a bijection

Every positive integer `e` has a unique representation:

```text
e = 2^a * q
```

where:

```text
a >= 0
```

and `q` is odd and positive.

Set:

```text
m = a + 1
```

and:

```text
v = (q + 1) / 2.
```

Then:

```text
pair(m,v) = e.
```

Uniqueness of the two-adic valuation and odd part makes `(m,v)` unique.

Therefore:

```text
pair : N+ × N+ <-> N+
```

is bijective.

The inverse is:

```text
unpair(e):
    a = v_2(e)
    q = e / 2^a

    m = a + 1
    v = (q + 1) / 2
```

where `v_2(e)` is the exponent of `2` in `e`.

---

## 7. LRPE interpretation

Define:

```text
LRPE(Z) = 1.
```

For:

```text
S = Node(M),
```

define:

```text
LRPE(S)
    =
∏[T ∈ supp(M)]
    p_{rank_M(T)}
    ^
    pair(mult_M(T), LRPE(T)).
```

Equivalently:

```text
E_LRPE(m,v)
=
pair(m,v).
```

Thus both multiplicity and recursive child value are encoded without collision
inside each prime exponent.

---

## 8. Structural admissibility

LRPE depends only on:

- SHAPES structural child classes;
- intrinsic multiplicities;
- a structural total order over those classes;
- recursively computed interpretation values.

It does not depend on:

- sibling occurrence position;
- traversal order;
- `OccurrencePath`;
- object identity;
- construction history;
- historical positional ranks.

Sibling permutations therefore leave the interpretation unchanged.

LRPE is structurally admissible under the current PETRA contract.

---

## 9. Totality

Every recursive call is made on a proper child form.

Every proper child has strictly smaller SHAPES size.

Therefore recursion terminates by induction on size.

For each finite node:

- support is finite;
- structural ranking is finite;
- every required prime index is finite;
- every paired exponent is positive and finite;
- the finite prime-power product is mathematically defined.

Hence LRPE is total on SHAPES.

---

## 10. Computability

Assuming a computable structural order, LRPE is computable.

Each node requires only:

1. finite structural comparison of distinct child forms;
2. finite prime generation;
3. recursive interpretation;
4. finite two-adic pairing;
5. finite integer exponentiation and multiplication.

This is a computability result, not an efficiency claim.

---

## 11. The PIP-2 collision is repaired

Recall:

```text
Z = Node(empty)
```

and:

```text
C = Node({Z}).
```

Then:

```text
LRPE(Z) = 1.
```

For `C`:

```text
pair(1,1)
=
1
```

so:

```text
LRPE(C)
=
2^1
=
2.
```

Now consider:

```text
S = Node({Z,Z})
```

and:

```text
T = Node({C}).
```

For `S`:

```text
pair(2,1)
=
2^(2-1) * (2*1-1)
=
2.
```

Hence:

```text
LRPE(S)
=
2^2
=
4.
```

For `T`:

```text
pair(1,2)
=
2^(1-1) * (2*2-1)
=
3.
```

Hence:

```text
LRPE(T)
=
2^3
=
8.
```

Therefore:

```text
LRPE(S) != LRPE(T).
```

The PIP-2 collision is eliminated.

This example alone does not prove global faithfulness.

That requires the next theorem.

---

## 12. Faithfulness theorem

### Theorem

```text
LRPE : SHAPES -> N+
```

is injective.

### Proof

Proceed by induction on SHAPES size.

The unique size-one form is:

```text
Z
```

with:

```text
LRPE(Z) = 1.
```

No non-zero-child form has value `1`, because every such form contains at
least one positive prime factor.

Now suppose faithfulness holds for all proper child forms of two forms:

```text
S = Node(M)
```

and:

```text
U = Node(N).
```

Assume:

```text
LRPE(S) = LRPE(U).
```

By unique prime factorization, both integers contain exactly the same prime
bases with exactly the same exponents.

Because local ranks are contiguous:

```text
1, ..., |supp(M)|
```

the factorization determines the same number of distinct child classes on both
sides.

For every local rank `r`, equality of the exponent at prime:

```text
p_r
```

gives:

```text
pair(mult_M(T_r), LRPE(T_r))
=
pair(mult_N(U_r), LRPE(U_r)).
```

Because `pair` is injective:

```text
mult_M(T_r)
=
mult_N(U_r)
```

and:

```text
LRPE(T_r)
=
LRPE(U_r).
```

By the inductive hypothesis:

```text
T_r = U_r.
```

Therefore each ranked child class is structurally equal and has equal
multiplicity.

Hence:

```text
M = N
```

as finite multisets.

Therefore:

```text
S = U.
```

Thus LRPE is faithful. QED.

---

## 13. Why the local ranks do not destroy faithfulness

Local rank by itself does not globally identify a child form.

For example, prime `2` merely means:

```text
first structurally ranked child class at this node.
```

That would be insufficient if the exponent contained only multiplicity.

LRPE remains faithful because the exponent also contains the recursively
faithful child value.

Factorization yields:

```text
local rank
+
paired(multiplicity, recursive value).
```

The recursive value identifies the child form inductively.

The rank therefore organizes the local factorization but does not carry the
entire identity burden.

---

## 14. Reachable image is not all positive integers

Faithfulness does not imply surjectivity.

LRPE has structural constraints on which prime factorizations are valid.

### Example: `3` is unreachable

Suppose a non-zero-child SHAPES form has exactly one distinct child class.

Its support rank set is:

```text
{1}.
```

Therefore its only prime base is:

```text
p_1 = 2.
```

Its value is consequently a positive power of `2`.

Now suppose a form has at least two distinct child classes.

Its local ranks include:

```text
1
```

and:

```text
2.
```

Therefore its prime factorization contains both:

```text
2
```

and:

```text
3.
```

Hence no SHAPES form can have value:

```text
3.
```

Therefore:

```text
Image(LRPE) != N+.
```

In particular:

```text
3 ∉ Image(LRPE).
```

LRPE is faithful but not surjective onto the positive integers.

---

## 15. Structural constraints on the reachable image

Every non-unit LRPE value has prime support equal to an initial prime segment:

```text
{p_1, p_2, ..., p_k}
```

for some:

```text
k >= 1.
```

Prime-support gaps are impossible.

For example:

```text
2^a * 5^b
```

with no factor `3` is unreachable.

However, contiguous prime support alone is not sufficient.

Each exponent must decode through `unpair` to:

```text
(m_r, v_r)
```

such that:

1. `m_r >= 1`;
2. `v_r` itself is a reachable LRPE value;
3. the decoded child forms are distinct;
4. their structural order agrees with their local ranks.

Therefore the image is recursively constrained.

---

## 16. Reverse interpretation on the image

Because LRPE is faithful, a reverse interpretation can be single-valued on its
reachable image.

Given:

```text
n = 1,
```

return:

```text
Z.
```

For:

```text
n > 1,
```

a candidate reverse procedure is:

1. factor `n`;
2. require prime support to be an initial segment:

   ```text
   p_1, ..., p_k;
   ```

3. for every exponent `e_r`, compute:

   ```text
   (m_r, v_r) = unpair(e_r);
   ```

4. recursively reverse each `v_r`;
5. require all decoded child forms to be structurally distinct;
6. require their structural order to agree with ranks `1,...,k`;
7. construct a root containing `m_r` copies of each decoded child form.

If any requirement fails:

```text
n ∉ Image(LRPE).
```

Thus LRPE naturally induces a partial reverse interpretation:

```text
LRPE^-1 : N+ ⇀ SHAPES.
```

It is total exactly on the reachable image.

---

## 17. Image membership is decidable

The reverse procedure of section 16 is not merely a recursive
characterization.

It terminates on every positive integer and therefore decides membership in
the LRPE image.

### Theorem — recursive reverse values decrease

Let:

```text
n > 1
```

and let:

```text
n = ∏ p_r ^ e_r
```

be its prime factorization.

Every exponent satisfies:

```text
2 ^ e_r <= n
```

because every prime base is at least `2`.

Therefore:

```text
e_r <= log_2(n).
```

Now decode:

```text
(m_r, v_r) = unpair(e_r).
```

By definition:

```text
e_r = 2^(m_r-1) * (2v_r-1).
```

Hence:

```text
2v_r - 1 <= e_r
```

and therefore:

```text
v_r <= (e_r + 1) / 2 <= e_r.
```

For every:

```text
n > 1,
```

we have:

```text
e_r < n.
```

Thus:

```text
v_r < n.
```

Every recursive reverse call therefore receives a strictly smaller positive
integer.

Since the positive integers are well-founded under `<`, unrestricted reverse
recursion terminates.

QED.

### Decision procedure

Define `decode_LRPE(n)` recursively.

For:

```text
n = 1,
```

return:

```text
Z.
```

For:

```text
n > 1,
```

perform the following finite procedure:

1. factor `n`;
2. require its prime support to be exactly an initial prime segment:

   ```text
   {p_1, ..., p_k};
   ```

3. for each exponent `e_r`, compute uniquely:

   ```text
   (m_r, v_r) = unpair(e_r);
   ```

4. recursively decode every `v_r`;
5. reject if any recursive value is outside the LRPE image;
6. reject if two decoded child forms are structurally equal;
7. order the decoded child forms by the fixed structural order `≺`;
8. reject unless that order agrees with their factor ranks:

   ```text
   1, ..., k;
   ```

9. construct:

   ```text
   Node(
       multiset containing
       m_r copies of the decoded rank-r child form
   ).
   ```

Every operation at one level is finite.

Every recursive call is made on:

```text
v_r < n.
```

Therefore the procedure terminates for every:

```text
n ∈ N+.
```

### Soundness

If:

```text
decode_LRPE(n) = S,
```

all local prime-support, exponent-pairing, recursive-image, distinctness, and
rank-consistency conditions have been verified.

Re-evaluating `S` under LRPE reconstructs exactly the original prime
factorization of `n`.

Therefore:

```text
LRPE(S) = n.
```

The decoder is sound.

### Completeness on the image

Suppose:

```text
n = LRPE(S)
```

for some SHAPES form `S`.

By construction of LRPE:

- its prime support is an initial prime segment;
- each exponent is exactly a valid paired `(multiplicity, recursive value)`;
- each recursive value is itself in the LRPE image;
- the child classes are structurally distinct;
- their structural order agrees with local prime ranks.

Therefore every validation step succeeds and recursive decoding reconstructs
the unique child forms by induction.

Hence:

```text
decode_LRPE(n) = S.
```

up to SHAPES structural equality.

The decoder is complete on the reachable image.

### Corollary — exact membership decision

For every positive integer `n`:

```text
n ∈ Image(LRPE)
```

if and only if:

```text
decode_LRPE(n)
```

succeeds.

Therefore:

```text
Image(LRPE)
```

is decidable.

### Corollary — effective inverse

Because LRPE is faithful and the decoder is sound and complete on its image:

```text
decode_LRPE
    =
LRPE^-1
```

on:

```text
Image(LRPE).
```

Thus LRPE admits an effective single-valued reverse interpretation on its
entire reachable image.

## 18. Comparison with Matula–Göbel

Matula–Göbel and LRPE are both:

- structurally admissible;
- total;
- computable;
- faithful.

They differ substantially in arithmetic semantics.

Matula–Göbel uses:

```text
prime index = recursive child value
exponent    = multiplicity
```

while LRPE uses:

```text
prime index = local structural rank
exponent    = pair(multiplicity, recursive child value).
```

Consequently:

```text
Image(MG)   = N+
```

whereas:

```text
Image(LRPE) ⊊ N+.
```

The two interpretations therefore are not observationally equivalent.

This is the first Phase 3 example of two faithful PETRA-compatible
interpretations with materially different arithmetic images.

---

## 19. PIP classification

```text
structurally admissible     YES
sibling-order invariant     YES
multiplicity explicit       YES

prime-valued                YES
locally prime-injective     YES

exponent pair-injective     YES
total                       YES
computable                  YES

faithful                    YES
collision-free              YES

reachable image             PROPER SUBSET OF N+
surjective onto N+          NO

reverse interpretation      SINGLE-VALUED ON IMAGE
image characterization      EXACT RECURSIVE
image decidability          YES
```

---

## 20. Research outcome

PIP-3 establishes that:

```text
local structural prime assignment
+
injective encoding of
(multiplicity, recursive child value)
```

is sufficient for global faithfulness.

The critical change from PIP-2 is not prime assignment.

It is preservation of the complete pair:

```text
(m,v).
```

Thus the sequence:

```text
PIP-2
E(m,v) = m*v
    ->
information loss
    ->
non-faithful
```

becomes:

```text
PIP-3
E(m,v) = pair(m,v)
    ->
pair information preserved
    ->
faithful.
```

At the same time, LRPE is not merely Matula–Göbel under different notation.

Its reachable arithmetic image is restricted by local-rank structure.

This gives PETRA a genuinely different interpretation candidate to study
without making it normative.
