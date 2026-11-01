# ASHES STE — Relative Historical Association Completeness

Status: THEORETICAL RESEARCH NOTE
Authority: nonnormative
Related experiment: EXP-004
EXP-007: NOT STARTED

## 1. Research question

Under which explicit assumptions can a finite enumeration
be proved complete relative to a declared historical
association model?

This note does not reconstruct actual history.

## 2. Information boundaries

FORM:
  SHAPES structure modulo the declared isomorphism.

CORRESPONDENCE:
  An occurrence mapping subject to its structural contract.

HISTORY:
  Externally supplied persistent identity or provenance.

SEMANTICS:
  Interpretation-owned content, policies and observables.

Structural equality, local array indices, canonical order
and TPI witnesses do not independently establish history.

## 3. Finite universe

Consider one root and two structurally indistinguishable
sibling occurrences, preserved across two branch states.

There are no births, deaths, reinsertion or MOVE.

Fix concrete occurrence sets:

  L = {l0, l1}
  R = {r0, r1}

The root is associated separately.

The finite universe U consists of all bijections L -> R:

  phi_id   = {(l0,r0), (l1,r1)}
  phi_swap = {(l0,r1), (l1,r0)}

Thus:

  U = {phi_id, phi_swap}

These names depend on the chosen local presentation.
Neither bijection is intrinsically historical identity.

In this restricted structural fixture both associations
are initially possible. Other structural contracts may
exclude candidates and must be declared separately.

## 4. Evidence model

Let E be a finite set of external constraints.

Positive attestations require occurrence associations.
Negative attestations exclude occurrence associations.

Each constraint is expressed on concrete occurrence
identifiers, not intrinsic SHAPES positions.

Define a total decidable predicate P_E on U:

  P_E(phi) =
      StructuralAdmissible(phi)
      AND all positive attestations hold under phi
      AND all negative attestations hold under phi

The model assumes the caller supplies the constraints
and declares their interpretation and reliability.

The verifier cannot establish whether an external
historical attestation is factually true.

Let:

  A_E = {phi in U : P_E(phi)}

## 5. Relative soundness and completeness

Let an enumerator visit every member of U exactly once
and include phi if and only if P_E(phi) is true.

Write its output as E_enum.

Soundness:

  For every phi in E_enum, P_E(phi) is true.
  Therefore E_enum is a subset of A_E.

Completeness:

  For every phi in A_E, phi belongs to U.
  The enumerator visits phi and includes it.
  Therefore A_E is a subset of E_enum.

Consequently:

  E_enum = A_E.

This is a direct finite proof, conditional on:
- U containing every candidate allowed by the model;
- the enumerator visiting every member of U;
- correct evaluation of the declared predicate.

It is NOT a proof that U exhausts real-world histories,
that the evidence is trustworthy, or that all admissible
historical models have been considered.

## 6. Controlled evidence examples

With all structural candidates admitted:

No discriminating attestations:
  A_E = {phi_id, phi_swap}

Attestation l0 -> r0:
  A_E = {phi_id}

Attestation l0 -> r1:
  A_E = {phi_swap}

Contradictory requirements l0 -> r0 and l0 -> r1:
  A_E = empty set.

The empty set A_E alone does not identify its cause.

Distinguish the consistency of external attestations
from joint satisfaction of attestations and structural
admissibility.

For this bounded bijection model, contradictory positive
requirements l0 -> r0 and l0 -> r1 cannot both hold in
any bijection, independently of structural admissibility.

Coherent attestations may nevertheless have no mapping
satisfying the additional structural restrictions.

This distinction requires an independently declared
evidence-consistency criterion. An empty A_E is not,
by itself, proof of a transformation conflict.

Missing, unverifiable or undecidable external evidence
does not justify a definitive historical conclusion.

## 7. Equivariance under relabeling

Let sigma_L and sigma_R be bijective renamings of the
concrete occurrence presentations in LEFT and RIGHT.

A historical association transforms as:

  phi' = sigma_R o phi o inverse(sigma_L)

The evidence constraints must be transported by the
same renaming.

The required property is:

  P_transported(phi') = P_E(phi).

Therefore the complete enumerated set transforms as:

  A_transported =
      {sigma_R o phi o inverse(sigma_L) : phi in A_E}.

The literal names phi_id and phi_swap may exchange.
The underlying association possibilities must not.

A future implementation must not select a candidate
merely from array position or enumeration order.

## 8. Material outcomes remain separate

Enumerating all admissible associations is not the
same as evaluating every reconciliation outcome.

Let O(phi) denote the requested material observable
under an explicitly declared interpretation.

Equal SteResult classifications do not by themselves
prove equal O(phi).

A claim of harmless multiplicity requires separate
evidence that material outcomes are equivalent.

In EXP-004, that equivalence remains a caller
assumption rather than an independently verified fact.

## 9. Relation to TPI and M001

A partial TPI correspondence must satisfy its own
root, ancestor-closure and direct-incidence conditions.

Historical identity is distinct and may persist through
a MOVE that does not preserve direct incidence.

This note does not replace either contract.

The endpoint-completeness theorem for witnessed edit
paths does not recover occurrence-survivor history.

No historical association is inferred solely from
SHAPES form equality or a preferred TPI witness.

## 10. Qualification and open questions

Established within the declared finite mathematical
model: conditional soundness and completeness of
enumeration by exhaustive predicate filtering.

Not established:
- factual reliability of historical attestations;
- completeness of the declared history model;
- autonomous discovery of persistent identities;
- exhaustive historical alternatives for EXP-004;
- independent verification of material equivalence;
- arbitrary-size enumeration or complexity bounds;
- general structural merge or semantic soundness.

EXP-004 historical completeness remains INCONCLUSIVE.
EXP-006 and its 69-check regression are unaffected.

No new executable evidence is asserted here.

## 11. Next research decision

Before any EXP-007 protocol or C11 implementation:

1. Decide whether the finite candidate universe is
   sufficient for the next falsifiable research question.
2. Specify the exact provenance and reliability contract
   of optional historical attestations.
3. Define how inconsistent evidence is distinguished
   from a coherent but unsatisfiable association model.
4. Declare the requested observable before evaluating
   equivalence of material outcomes.

No normative SHAPES or TPI promotion is authorized.

## References

- docs/research/ste-m001-contract.md
- tools/research/ste_001/EXP004_PROTOCOL.md
- docs/research/theory/local-edit-path-completeness.md
- tools/research/tpi_algebra/move_002/FORMAL_NOTES.md
