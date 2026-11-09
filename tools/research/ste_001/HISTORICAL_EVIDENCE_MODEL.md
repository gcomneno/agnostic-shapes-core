# ASHES STE — Historical Evidence Model

Status: THEORETICAL RESEARCH NOTE — ISSUE #411
Authority: nonnormative
Implementation: none
EXP-007: not started

## 1. Research question

What external evidence contract can justify or exclude
historical occurrence associations while distinguishing
consistency, sufficiency and provenance?

This note refines the HISTORY information level of
STE-M001. It does not reconstruct actual history.

## 2. Information boundaries

FORM:
  SHAPES structure modulo rooted-tree isomorphism.

CORRESPONDENCE:
  An explicit occurrence mapping subject to its
  separately declared structural contract.

HISTORY:
  Optional externally supplied persistent identities,
  association attestations and operation provenance.

SEMANTICS:
  Interpretation-owned content, policy and observables.

Neither form equality, canonical order, local indices
nor a TPI witness establishes historical identity.

A TPI complement is not automatically evidence of
historical birth or death.

## 3. Occurrence domain

Let L and R be finite sets of concrete occurrences
belonging to two explicitly identified snapshots.

Occurrence handles identify elements only within
their declared snapshot. Their textual or numeric
representation carries no historical meaning.

Let U_H be a declared nonempty finite universe of
candidate historical associations between L and R.

The association class must be specified explicitly:
for example, total bijections in a preserved-occurrence
fixture, or partial mappings in a different model.

U_H represents the historical candidate domain
*before* applying additional TPI or STE structural
admissibility restrictions.

The completeness of U_H relative to real histories
is an external model assumption, not a theorem here.

## 4. Attestations and provenance

An association attestation is a record:

  e = (source, target, polarity, provenance)

where:

  source:
    an occurrence in L

  target:
    an occurrence in R

  polarity:
    REQUIRE or EXCLUDE the stated association

  provenance:
    the explicitly declared origin and trust assumptions
    for this assertion

An actual evidence record should additionally permit
an unambiguous record identifier and an assessment
of whether its claim is accepted, rejected or unresolved.

Provenance describes why a caller considers a record
usable; its presence does not prove historical truth.

Reliability is not inferred from the structure of
L or R, from TPI, or from the numeric identifiers.

The selection of accepted attestations is externally
owned and must be disclosed as an assumption.

Let Assess_E be a caller-supplied assessment procedure
over evidence records, with declared provenance rules,
scope, required inputs and trust assumptions.

Its possible outcomes are:

  ACCEPTED:
    The record is admitted as a historical constraint.

  REJECTED:
    The record is not admitted; its negation is not
    thereby established.

  UNRESOLVED:
    The procedure cannot justify acceptance or rejection
    under its declared requirements.

E_acc contains exactly the accepted records. The caller
must expose the assessment assumptions and unresolved
records whenever making a historical conclusion.

This procedure is a contract boundary, not an intrinsic
SHAPES operation or a proof of factual reliability.

## 5. Satisfaction and evidence consistency

For phi in U_H, define:

  phi satisfies REQUIRE(s,t)
    iff (s,t) belongs to phi

  phi satisfies EXCLUDE(s,t)
    iff (s,t) does not belong to phi

Let E_acc be the finite set of accepted attestations.

Define:

  C_E = {phi in U_H :
         phi satisfies every e in E_acc}

  Consistent(E_acc, U_H)
    iff C_E is nonempty

This consistency criterion deliberately excludes
additional SHAPES/TPI structural admissibility tests.

It is relative to the declared association universe:
an unjustifiably narrow U_H can make evidence appear
inconsistent even when a broader model admits it.

Consistency does not establish the factual truth
of the accepted attestations.

## 6. Structural satisfiability is separate

Let StructuralAdmissible(phi) be a separately declared
structural predicate over candidates in U_H.

Define:

  A_E = {phi in C_E :
         StructuralAdmissible(phi)}

The following situations must remain distinct.

EVIDENCE_INCONSISTENT:
  C_E is empty.

STRUCTURALLY_UNSATISFIABLE:
  C_E is nonempty, but A_E is empty.

ADMISSIBLE_CANDIDATES:
  A_E is nonempty.

The empty set A_E alone cannot identify its cause.

Neither evidence inconsistency nor structural
unsatisfiability automatically proves that the
branch transformations themselves conflict.

Any mapping to STE result classes requires the
independently declared reconciliation contract.

## 7. Missing and uncertain evidence

The historical evidence model is open-world:

  Absence of REQUIRE(s,t) does not imply EXCLUDE(s,t).

Missing evidence:
  No relevant record has been supplied.

Unverifiable evidence:
  A record exists but its factual provenance or
  reliability cannot be established as required.

Undecidable assessment:
  The declared acceptance or validation procedure
  cannot determine whether to accept a record.

Rejected evidence:
  A record is explicitly not admitted into E_acc;
  rejection does not automatically supply its negation.

A negative attestation is an explicit EXCLUDE assertion,
not simply the absence or rejection of a REQUIRE record.

Unresolved evidence must not silently be converted
into a positive or negative attestation.

The assessment procedure may use externally declared
provenance or reliability requirements. The research
model neither assigns trust scores nor invents missing
provenance.

Unresolved records remain visible outside E_acc.
Their possible later acceptance must not be represented
as an already established historical fact.

Where unresolved evidence is required for the requested
historical conclusion, that conclusion is unsupported
or inconclusive at the research-evidence level.

## 8. Consistency is not sufficiency

Let Q be a declared historical query, and let
Answer_Q(phi) be its answer for candidate phi.

Evidence is sufficient to decide Q only if:

  C_E is nonempty;

  Answer_Q is defined for all candidates in C_E;

  all candidates in C_E yield the same answer.

This is conditional sufficiency relative to U_H,
the currently accepted E_acc and the declared query Q.

It does not establish robustness under future changes
to the accepted evidence set.

Robust sufficiency would require separately declaring
which resolutions of unresolved records are permitted
and verifying the query result across every permitted
consistent resolution.

No general robust-sufficiency theorem is asserted here.
If an unresolved record may change the requested answer,
conditional sufficiency must not be presented as an
unqualified historical conclusion.

If the requested query additionally requires structural
admissibility, its candidate domain and prerequisites
must be declared separately.

Even unanimous answers cannot validate incorrect
external attestations or an incomplete U_H.

A decision about historical association does not
by itself establish semantic compatibility or
equivalence of material reconciliation outcomes.

## 9. Finite controlled examples

Let:

  L = {l0,l1}
  R = {r0,r1}

and let U_H contain both bijections:

  id   = {(l0,r0),(l1,r1)}
  swap = {(l0,r1),(l1,r0)}

With no accepted attestations:

  C_E = {id,swap}

With REQUIRE(l0,r0):

  C_E = {id}

With EXCLUDE(l0,r0):

  C_E = {swap}

With REQUIRE(l0,r0) and REQUIRE(l0,r1):

  C_E = empty

This last contradiction follows from the declared
bijection contract. It does not follow from SHAPES
form equality or a TPI witness.

With coherent evidence admitting id only, and an
independently declared structural predicate rejecting id:

  C_E = {id}
  A_E = empty

Thus structural unsatisfiability and evidence
inconsistency have different causes.

## 10. Representation invariance

Let sigma_L and sigma_R be bijective renamings of
the local occurrence representations.

Transport a candidate phi by:

  phi' = sigma_R o phi o inverse(sigma_L)

Transport every accepted attestation accordingly.

The satisfaction relation must be invariant under
this simultaneous transport.

Consistency, sufficiency and admissibility conclusions
must not depend on local array indices, enumeration
order or arbitrary names for symmetric occurrences.

## 11. Permitted claims and limitations

Under the explicitly declared universe, accepted
evidence and satisfaction relation, consistency and
query-relative sufficiency are mathematically defined.

The model does not establish:

- truth or reliability of external attestations;
- soundness of the caller-supplied assessment procedure;
- robust sufficiency under unresolved evidence;
- completeness of U_H over actual historical events;
- automatic persistent-identity discovery;
- TPI validity of any historical mapping;
- semantic equivalence of material results;
- general merge soundness or completeness;
- concurrency, CRDT or production behavior.

EXP-004 historical completeness remains INCONCLUSIVE.

The relative-enumeration theorem in
HISTORICAL_COMPLETENESS_NOTE.md remains conditional
on its stated universe and admissibility predicate.

No executable evidence is claimed here.

## 12. Research handoff

R02 may use this evidence contract to define a
larger finite candidate universe and its enumeration.

R03 owns material-outcome equivalence.

R04 owns the permitted uses of TPI constraints.

EXP-007 requires a separate frozen protocol before
any C11 implementation.

No normative SHAPES or TPI promotion is authorized.

## References

- docs/research/ste-m001-contract.md
- tools/research/ste_001/EXP004_PROTOCOL.md
- tools/research/ste_001/HISTORICAL_COMPLETENESS_NOTE.md
- docs/research/theory/local-edit-path-completeness.md
- tools/research/tpi_algebra/move_002/FORMAL_NOTES.md
