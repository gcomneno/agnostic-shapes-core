# ASHES STE — Finite Historical Association Models

Status: THEORETICAL RESEARCH NOTE — ISSUE #412
Authority: nonnormative
Prerequisite: R01 / issue #411
Implementation: none
EXP-007: not started

## 1. Research question

Under which declared finite-domain assumptions can every
admissible historical association be enumerated, and can
soundness, completeness and representation equivariance
be justified independently of a particular implementation?

Completeness is relative to a model, never an assertion
that the model contains every actual historical account.

## 2. Information boundaries

FORM is the underlying SHAPES structural carrier.

CORRESPONDENCE is an explicit mapping with a separately
specified structural validity discipline.

HISTORY consists of externally supplied historical
associations and provenance.

SEMANTICS belongs to the interpretation.

No equality of forms, local indices, canonical ordering,
or selected TPI witness establishes persistent identity.

## 3. Finite association family

Let L and R be finite, disjointly tagged sets of concrete
occurrences belonging to two identified snapshots.

Let:

  Rel(L,R) = P(L x R)

be the finite universe of all binary relations between
these occurrence sets.

An association-class predicate H, fixed before evaluating
evidence or outputs, declares which relations belong to
the chosen historical candidate model.

Define:

  U_H = {phi in Rel(L,R) : H(phi)}

Assume U_H is nonempty.

The model declares whether H requires a total bijection,
a partial injective association or another explicit
relation class. It also declares treatment of the root,
unmatched occurrences, cardinality and preservation.

H is not inferred from desired reconciliation outcomes.
The full relation universe must not be pruned in response
to observed classifier results.

U_H is defined independently of the enumeration algorithm.

## 4. Evidence and structural predicates

Let E_acc be the externally accepted attestation set
under the R01 historical-evidence contract.

Define EvidenceSatisfied(phi,E_acc) using the declared
REQUIRE and EXCLUDE satisfaction relation.

Let S be a separately declared total decidable predicate
on U_H. It represents the additional structural
admissibility conditions chosen for the present study.

S is deliberately abstract here.

No TPI witness, historical identity assertion or MOVE
condition is silently built into S.

Define:

  C_E = {phi in U_H :
         EvidenceSatisfied(phi,E_acc)}

  A_E = {phi in C_E : S(phi)}

Evidence consistency is the condition C_E != empty.

Structural unsatisfiability in a coherent evidence model
occurs when C_E != empty and A_E = empty.

Neither case alone establishes transformation conflict.

Assessment of unresolved evidence and the reliability
of accepted attestations remain governed by R01.

## 5. Exhaustive reference construction

Because L and R are finite, L x R is finite.

Fix any ordering of its pairs solely for enumeration.
Every bit vector of length |L x R| determines exactly
one relation in Rel(L,R), by selecting its set bits.

Enumerate all such bit vectors.

For each generated relation phi:

  1. retain it only if H(phi);
  2. retain it only if EvidenceSatisfied(phi,E_acc);
  3. retain it only if S(phi).

Call the resulting collection E_enum.

The selected order is an implementation convention and
does not determine identity, candidate preference or
historical meaning.

This reference construction is mathematical. No C11
enumerator or executable qualification is asserted.

## 6. Relative soundness

Take any phi in E_enum.

The construction retained phi only after verifying
H(phi), EvidenceSatisfied(phi,E_acc) and S(phi).

Therefore phi belongs to U_H, C_E and A_E.

Hence:

  E_enum subseteq A_E.

## 7. Relative completeness

Take any phi in A_E.

Then phi is a relation in Rel(L,R), with H(phi) true,
EvidenceSatisfied(phi,E_acc) true and S(phi) true.

Every relation has exactly one bit-vector encoding
relative to the chosen enumeration ordering.

The exhaustive construction visits that encoding and
retains phi because all three predicates hold.

Therefore phi belongs to E_enum.

Hence:

  A_E subseteq E_enum.

Combining both inclusions:

  E_enum = A_E.

The proof requires:
- finite concrete occurrence sets;
- exhaustive traversal of all relation encodings;
- correct and total evaluation of H, evidence and S;
- stable declared predicates during enumeration.

The theorem does not hold operationally if any required
predicate is unresolved, partial or not evaluable.

A model-relative completeness theorem does not prove
that H or U_H captures all real historical possibilities.

## 8. Two-occurrence specialization

Let:

  L = {l0,l1}
  R = {r0,r1}

Let H admit exactly the total bijections.

Then U_H contains:

  id   = {(l0,r0),(l1,r1)}
  swap = {(l0,r1),(l1,r0)}

If E_acc is empty and S accepts both, then:

  A_E = {id,swap}.

If REQUIRE(l0,r0) is accepted and S accepts both,
then A_E contains id only.

This recovers the bounded relative result in
HISTORICAL_COMPLETENESS_NOTE.md without amending it.

## 9. Three-occurrence instance

Let:

  L = {l0,l1,l2}
  R = {r0,r1,r2}

Let H admit all total bijections and assume the root
has already been treated outside these occurrence sets.

There are 3! = 6 bijections.

With no accepted evidence and S identically true,
all six remain admissible.

With the accepted REQUIRE(l0,r0), two bijections
remain: the two permutations of the remaining pair.

Adding REQUIRE(l1,r1) leaves exactly one bijection.

With REQUIRE(l0,r0) and REQUIRE(l0,r1),
the accepted evidence is inconsistent relative
to the declared bijection model.

With evidence admitting exactly one bijection phi,
and S(phi) false, C_E is nonempty while A_E is empty.

These are finite mathematical examples, not test runs.

## 10. Independent renumbering

Let sigma_L and sigma_R be bijective renamings of the
two concrete occurrence presentations.

The transport of phi is:

  T(phi) = sigma_R o phi o inverse(sigma_L)

For relational candidates, this denotes transporting
every ordered pair, not assuming phi is a function.

Require transported predicates to satisfy:

  H'(T(phi)) = H(phi)

  EvidenceSatisfied'(T(phi),E_acc')
    = EvidenceSatisfied(phi,E_acc)

  S'(T(phi)) = S(phi)

Under these assumptions T induces bijections between
U_H and U_H', and between A_E and A_E'.

Consequently:

  A_E' = {T(phi) : phi in A_E}.

This is equivariance under representation changes.

The assumptions must be checked for any concrete
instantiation; an arbitrary predicate S need not be
equivariant automatically.

Enumeration order and local array positions cannot
legitimately select one association from A_E.

## 11. Relationship to TPI

TPI conditions may instantiate part of S only when
their applicability is declared.

Historical association phi and TPI witness w need
not be identical.

A genuine historical MOVE may preserve vertex identity
while changing parent incidence, so requiring
TPIValid(phi) without qualification could exclude
historically legitimate associations.

Issue #414 owns the precise TPI/HISTORY interface.

This note does not establish a total TPI residual,
historical identity reconstruction or a stable STE API.

## 12. What the result does not prove

The theorem does not establish:

- factual reliability of external attestations;
- completeness of the model against actual history;
- automatic discovery of persistent identities;
- semantic correctness of reconciliation outcomes;
- equality of material results for different mappings;
- any complexity guarantee for arbitrary implementations;
- general merge soundness or completeness;
- concurrency, CRDT or production-readiness.

In particular, EXP-004 historical completeness remains
INCONCLUSIVE because its externally supplied alternatives
were not proved exhaustive against a historical model.

R03 owns equivalence of material outcomes.

The 69/69 C11 regression previously qualified under
EXP-006 is unchanged and is not rerun for this note.

## 13. Research handoff

R04 can refine the abstract structural predicate S
through an explicit TPI/HISTORY interface.

R03 can compare outcomes over the same A_E after a
requested observable and equivalence are declared.

EXP-007 may investigate a bounded C11 enumerator only
after a separate protocol with frozen inputs, expected
outputs, falsification criteria and outcome classes.

No implementation or normative promotion is authorized.

## References

- docs/research/ste-m001-contract.md
- tools/research/ste_001/HISTORICAL_EVIDENCE_MODEL.md
- tools/research/ste_001/HISTORICAL_COMPLETENESS_NOTE.md
- tools/research/ste_001/EXP004_PROTOCOL.md
- docs/research/theory/local-edit-path-completeness.md
